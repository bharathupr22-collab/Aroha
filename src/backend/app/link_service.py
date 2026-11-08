import ipaddress
import os
import re
import socket
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import httpx

# Optional heavy multimodal imports (graceful fallback if model weights aren't cached yet)
try:
    import cv2
except ImportError:
    cv2 = None

try:
    import easyocr
except ImportError:
    easyocr = None

try:
    import whisper
except ImportError:
    whisper = None

URL_REGEX = re.compile(
    r"(?:https?://|www\.)[^\s<>\"'\]\)]+|"
    r"\b(?:[a-zA-Z0-9-]+\.)+(?:com|in|org|net|io|co|shop|store|link|bio|me|ly|gl|to|app|xyz)(?:/[^\s<>\"'\]\)]*)?",
    re.IGNORECASE,
)

PROMO_KEYWORDS = {
    "discount", "promo", "offer", "sale", "coupon", "code", "affiliate",
    "partner", "sponsored", "ad", "bio", "link in bio", "shop", "buy",
    "deal", "limited", "checkout", "store", "order", "free shipping", "off"
}

SUSPICIOUS_TLDS = {".zip", ".mov", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click"}
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "rebrand.ly", "cutt.ly", "shorturl.at", "linktr.ee"
}


class LinkAnalyzerService:
    _ocr_reader = None
    _whisper_model = None

    @classmethod
    def get_ocr_reader(cls):
        if cls._ocr_reader is None and easyocr is not None:
            try:
                cls._ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            except Exception:
                cls._ocr_reader = None
        return cls._ocr_reader

    @classmethod
    def get_whisper_model(cls):
        if cls._whisper_model is None and whisper is not None:
            try:
                cls._whisper_model = whisper.load_model("base")
            except Exception:
                cls._whisper_model = None
        return cls._whisper_model

    @staticmethod
    def normalize_url(raw_url: str) -> str:
        cleaned = raw_url.strip().rstrip(".,;:!?)>\"'")
        if not cleaned.lower().startswith(("http://", "https://")):
            cleaned = f"https://{cleaned}"
        return cleaned

    @classmethod
    def extract_urls(cls, text: Optional[str]) -> List[str]:
        if not text:
            return []
        # Strip email addresses so they are not mistaken for domain URLs
        cleaned_text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "", text)
        matches = URL_REGEX.findall(cleaned_text)
        seen: Set[str] = set()
        results: List[str] = []
        for match in matches:
            norm = cls.normalize_url(match)
            if norm not in seen:
                seen.add(norm)
                results.append(norm)
        return results

    @staticmethod
    def is_promotional_context(text: Optional[str], url: str) -> bool:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if any(short in host for short in SHORTENER_DOMAINS):
            return True
        if not text:
            return True
        lower_text = text.lower()
        return any(kw in lower_text for kw in PROMO_KEYWORDS)

    @staticmethod
    def is_ssrf_safe(url: str) -> tuple[bool, Optional[str]]:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False, "Unsupported URL scheme (only HTTP/HTTPS allowed)."
            hostname = parsed.hostname
            if not hostname:
                return False, "Missing hostname in URL."
            lower_host = hostname.lower().strip()
            if lower_host in {"localhost", "127.0.0.1", "0.0.0.0", "::1", "local"}:
                return False, "SSRF Protection: Localhost access is blocked."

            # Check if host is a raw IP literal
            try:
                raw_ip = ipaddress.ip_address(lower_host)
                if (
                    raw_ip.is_private
                    or raw_ip.is_loopback
                    or raw_ip.is_link_local
                    or raw_ip.is_multicast
                    or raw_ip.is_reserved
                    or raw_ip.is_unspecified
                ):
                    return False, f"SSRF Protection: Restricted internal IP ({raw_ip}) blocked."
                return True, None
            except ValueError:
                pass

            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                if (
                    ip_obj.is_private
                    or ip_obj.is_loopback
                    or ip_obj.is_link_local
                    or ip_obj.is_multicast
                    or ip_obj.is_reserved
                    or ip_obj.is_unspecified
                ):
                    return False, f"SSRF Protection: Restricted internal IP ({ip_str}) blocked."
            return True, None
        except socket.gaierror:
            return False, "DNS Resolution Failed: Domain does not exist or cannot be reached."
        except Exception as exc:
            return False, f"URL validation error: {str(exc)}"

    @classmethod
    def check_suspicious_url(cls, url: str) -> Optional[str]:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        for tld in SUSPICIOUS_TLDS:
            if host.endswith(tld):
                return f"Suspicious top-level domain ({tld}) flagged for potential phishing."
        if "@" in url:
            return "URL contains embedded credentials (@ symbol), common in phishing links."
        return None

    @classmethod
    def validate_url(
        cls,
        url: str,
        source_type: str = "caption",
        context_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        norm_url = cls.normalize_url(url)
        is_promo = cls.is_promotional_context(context_text, norm_url)
        suspicious_reason = cls.check_suspicious_url(norm_url)

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        start_time = time.perf_counter()
        current_url = norm_url
        redirect_chain: List[str] = [norm_url]
        redirect_count = 0
        final_url = norm_url
        status: Optional[int] = None

        with httpx.Client(timeout=8.0, headers=headers) as client:
            while True:
                # 1. Evaluate SSRF safety of current hop before opening connection
                is_safe, ssrf_reason = cls.is_ssrf_safe(current_url)
                if not is_safe:
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    is_dns = ssrf_reason and "DNS Resolution Failed" in ssrf_reason
                    is_hop_redirect = redirect_count > 0
                    return {
                        "detected_url": norm_url,
                        "final_url": current_url,
                        "source_type": source_type,
                        "is_promotional": is_promo,
                        "response_status": status,
                        "validation_result": "suspicious" if is_hop_redirect else ("broken" if is_dns else "suspicious"),
                        "error_category": "unsafe_redirect" if is_hop_redirect else ("dns_failure" if is_dns else "ssrf_blocked"),
                        "issue_description": f"Redirect hop {redirect_count} blocked: {ssrf_reason}" if is_hop_redirect else ssrf_reason,
                        "redirect_count": redirect_count,
                        "redirect_chain": redirect_chain,
                        "response_time_ms": elapsed_ms,
                        "analysis_report": {
                            "redirect_chain": redirect_chain,
                            "redirect_count": redirect_count,
                            "response_time_ms": elapsed_ms,
                            "final_url": current_url,
                            "blocked_reason": ssrf_reason,
                        },
                        "checked_at": datetime.now(timezone.utc),
                    }

                # 2. Execute single request hop with follow_redirects=False
                try:
                    response = client.get(current_url, follow_redirects=False)
                    status = response.status_code
                    final_url = str(response.url)

                    # 3. Check for redirect responses (301, 302, 303, 307, 308)
                    if response.is_redirect and "location" in response.headers:
                        redirect_count += 1
                        next_url = str(urljoin(current_url, response.headers["location"]))
                        if redirect_count > 6:
                            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                            return {
                                "detected_url": norm_url,
                                "final_url": final_url,
                                "source_type": source_type,
                                "is_promotional": is_promo,
                                "response_status": status,
                                "validation_result": "broken",
                                "error_category": "redirect_loop",
                                "issue_description": f"Exceeded maximum redirect limit (6 hops) in chain: {' -> '.join(redirect_chain)}",
                                "redirect_count": redirect_count,
                                "redirect_chain": redirect_chain,
                                "response_time_ms": elapsed_ms,
                                "analysis_report": {
                                    "redirect_chain": redirect_chain,
                                    "redirect_count": redirect_count,
                                    "response_time_ms": elapsed_ms,
                                    "final_url": final_url,
                                },
                                "checked_at": datetime.now(timezone.utc),
                            }
                        if next_url in redirect_chain:
                            redirect_chain.append(next_url)
                            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                            return {
                                "detected_url": norm_url,
                                "final_url": next_url,
                                "source_type": source_type,
                                "is_promotional": is_promo,
                                "response_status": status,
                                "validation_result": "broken",
                                "error_category": "redirect_loop",
                                "issue_description": f"Circular redirect loop detected: {next_url} revisited in chain: {' -> '.join(redirect_chain)}",
                                "redirect_count": redirect_count,
                                "redirect_chain": redirect_chain,
                                "response_time_ms": elapsed_ms,
                                "analysis_report": {
                                    "redirect_chain": redirect_chain,
                                    "redirect_count": redirect_count,
                                    "response_time_ms": elapsed_ms,
                                    "final_url": next_url,
                                },
                                "checked_at": datetime.now(timezone.utc),
                            }
                        redirect_chain.append(next_url)
                        current_url = next_url
                        continue

                    # 4. Terminal response reached
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    hop_suspicious = cls.check_suspicious_url(final_url) or suspicious_reason
                    if hop_suspicious:
                        return {
                            "detected_url": norm_url,
                            "final_url": final_url,
                            "source_type": source_type,
                            "is_promotional": is_promo,
                            "response_status": status,
                            "validation_result": "suspicious",
                            "error_category": "suspicious_domain",
                            "issue_description": hop_suspicious,
                            "redirect_count": redirect_count,
                            "redirect_chain": redirect_chain,
                            "response_time_ms": elapsed_ms,
                            "analysis_report": {
                                "redirect_chain": redirect_chain,
                                "redirect_count": redirect_count,
                                "response_time_ms": elapsed_ms,
                                "final_url": final_url,
                                "suspicious_reason": hop_suspicious,
                            },
                            "checked_at": datetime.now(timezone.utc),
                        }

                    if 200 <= status < 400:
                        desc = (
                            f"Resolved cleanly ({status} OK)"
                            if redirect_count == 0
                            else f"Valid after {redirect_count} redirect(s) -> {final_url}"
                        )
                        return {
                            "detected_url": norm_url,
                            "final_url": final_url,
                            "source_type": source_type,
                            "is_promotional": is_promo,
                            "response_status": status,
                            "validation_result": "working",
                            "error_category": None,
                            "issue_description": desc,
                            "redirect_count": redirect_count,
                            "redirect_chain": redirect_chain,
                            "response_time_ms": elapsed_ms,
                            "analysis_report": {
                                "redirect_chain": redirect_chain,
                                "redirect_count": redirect_count,
                                "response_time_ms": elapsed_ms,
                                "final_url": final_url,
                            },
                            "checked_at": datetime.now(timezone.utc),
                        }

                    error_cat = "http_404" if status == 404 else (
                        "http_5xx" if status >= 500 else f"http_{status}"
                    )
                    return {
                        "detected_url": norm_url,
                        "final_url": final_url,
                        "source_type": source_type,
                        "is_promotional": is_promo,
                        "response_status": status,
                        "validation_result": "broken",
                        "error_category": error_cat,
                        "issue_description": f"Destination returned HTTP {status} error response.",
                        "redirect_count": redirect_count,
                        "redirect_chain": redirect_chain,
                        "response_time_ms": elapsed_ms,
                        "analysis_report": {
                            "redirect_chain": redirect_chain,
                            "redirect_count": redirect_count,
                            "response_time_ms": elapsed_ms,
                            "final_url": final_url,
                        },
                        "checked_at": datetime.now(timezone.utc),
                    }

                except httpx.TimeoutException:
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    return {
                        "detected_url": norm_url,
                        "final_url": current_url,
                        "source_type": source_type,
                        "is_promotional": is_promo,
                        "response_status": None,
                        "validation_result": "broken",
                        "error_category": "timeout",
                        "issue_description": "Connection timed out after 8 seconds.",
                        "redirect_count": redirect_count,
                        "redirect_chain": redirect_chain,
                        "response_time_ms": elapsed_ms,
                        "analysis_report": {
                            "redirect_chain": redirect_chain,
                            "redirect_count": redirect_count,
                            "response_time_ms": elapsed_ms,
                            "final_url": current_url,
                        },
                        "checked_at": datetime.now(timezone.utc),
                    }
                except Exception as exc:
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    return {
                        "detected_url": norm_url,
                        "final_url": current_url,
                        "source_type": source_type,
                        "is_promotional": is_promo,
                        "response_status": None,
                        "validation_result": "broken",
                        "error_category": "connection_error",
                        "issue_description": f"Unreachable promotional endpoint: {str(exc)}",
                        "redirect_count": redirect_count,
                        "redirect_chain": redirect_chain,
                        "response_time_ms": elapsed_ms,
                        "analysis_report": {
                            "redirect_chain": redirect_chain,
                            "redirect_count": redirect_count,
                            "response_time_ms": elapsed_ms,
                            "final_url": current_url,
                        },
                        "checked_at": datetime.now(timezone.utc),
                    }

    @classmethod
    def extract_video_multimodal_urls(cls, video_path: str) -> Dict[str, List[str]]:
        """Extracts URLs from video frames (OCR + QR codes) and speech (Whisper)."""
        found: Dict[str, List[str]] = {"ocr": [], "qr": [], "audio_transcript": []}
        if not video_path or not os.path.exists(video_path):
            return found

        if cv2 is not None:
            cap = cv2.VideoCapture(video_path)
            qr_detector = cv2.QRCodeDetector()
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            frame_interval = max(int(fps * 2), 1)  # sample 1 frame every 2 seconds
            frame_idx = 0
            ocr_reader = cls.get_ocr_reader()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % frame_interval == 0:
                    # 1. QR Code Detection
                    try:
                        qr_data, _, _ = qr_detector.detectAndDecode(frame)
                        if qr_data:
                            for u in cls.extract_urls(qr_data):
                                if u not in found["qr"]:
                                    found["qr"].append(u)
                    except Exception:
                        pass

                    # 2. Frame OCR Text Detection
                    if ocr_reader is not None:
                        try:
                            texts = ocr_reader.readtext(frame, detail=0)
                            joined = " ".join(texts)
                            for u in cls.extract_urls(joined):
                                if u not in found["ocr"]:
                                    found["ocr"].append(u)
                        except Exception:
                            pass
                frame_idx += 1
            cap.release()

        # 3. Whisper Audio Speech-to-Text URL Extraction
        whisper_model = cls.get_whisper_model()
        if whisper_model is not None:
            try:
                result = whisper_model.transcribe(video_path, fp16=False)
                transcript = result.get("text", "")
                for u in cls.extract_urls(transcript):
                    if u not in found["audio_transcript"]:
                        found["audio_transcript"].append(u)
            except Exception:
                pass

        return found


# =====================================================================
# Functional and Backwards-Compatible Service Helpers
# =====================================================================
def is_safe_host(host: str) -> bool:
    """Validate that a host resolves to a public, non-reserved IP address (SSRF safe)."""
    try:
        lower_host = host.lower().strip()
        if lower_host in {"localhost", "127.0.0.1", "0.0.0.0", "::1", "local"}:
            return False
        try:
            raw_ip = ipaddress.ip_address(lower_host)
            if (
                raw_ip.is_private
                or raw_ip.is_loopback
                or raw_ip.is_link_local
                or raw_ip.is_reserved
                or raw_ip.is_multicast
                or raw_ip.is_unspecified
            ):
                return False
            return True
        except ValueError:
            pass

        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return False
    return True


def extract_urls(text: str) -> List[str]:
    """Extract and normalize all URLs and promotional links from text."""
    return LinkAnalyzerService.extract_urls(text)


def check_url(url: str) -> tuple[Optional[int], str, Optional[str]]:
    """Return (status_code, result, issue). result: working|broken|redirect_loop|unsafe|invalid|unreachable."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None, "invalid", "Not a valid http(s) URL"
    if not is_safe_host(parsed.hostname):
        return None, "unreachable", "Host could not be resolved or is not a public address"
    res = LinkAnalyzerService.validate_url(url)
    return res.get("response_status"), res.get("validation_result", "broken"), res.get("issue_description")
