"""Builds docs/AROHA_Synopsis.docx from the college synopsis template.

Run (from docs/_build):  python build_synopsis.py
"""
import os
import shutil

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

from docx_helpers import (Builder, add_field, add_marked_runs, enable_update_fields_on_open, set_paragraph_text,
                          style_run, trim_body)

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
TEMPLATE = os.path.expanduser("~/Downloads/Major Project - Synopsis report.docx")
OUT = os.path.join(HERE, "..", "AROHA_Synopsis.docx")

TITLE = "AROHA: An AI-Assisted Instagram Analytics and Multimedia Content Integrity Monitoring Platform"
STUDENT, USN = "Karthik Pai", "4MT25MC041"
GUIDE, DESIG = "Dr. Chandrakantha T S", "Assistant Professor"

TOC = [
    ("title", "Title", "Final project title"),
    ("intro", "Introduction / Background", "Domain context and the gap in creator tools"),
    ("problem", "Problem Statement", "The unsolved problem in brief"),
    ("motivation", "Motivation", "Why the problem matters"),
    ("lit", "Literature Survey", "Review of thirteen related works and sources"),
    ("gap", "Research / Technical Gap", "Six gaps addressed by the project"),
    ("objectives", "Objectives", "Six measurable objectives"),
    ("method", "Proposed Methodology", "Eight-step development and evaluation plan"),
    ("arch", "Proposed System / Architecture", "Layers, modules and data flow"),
    ("dataset", "Dataset / Data Sources", "Data used and evaluation dataset plan"),
    ("tech", "Technology Stack", "Languages, libraries, storage and tools"),
    ("outcomes", "Expected Outcomes", "Tangible deliverables"),
    ("novelty", "Innovation / Novelty", "Points of differentiation"),
    ("limits", "Limitations / Future Work", "Scope constraints and extensions"),
    ("refs", "References", "Sources cited in this synopsis"),
]

# --------------------------------------------------------------------------- content
INTRO = [
    "Instagram has become one of the main channels through which creators and small businesses promote products, "
    "publish short-form video and build audiences. Meta's official Instagram Platform lets professional (Business and "
    "Creator) accounts authorise third-party applications to read account insights and media metadata. The data it "
    "exposes, however, is limited in scope and retention, and it describes account performance rather than the quality "
    "of the content itself. Creators therefore still check many problems by hand: a link in a bio or Reel may stop "
    "working, the audio of a video may be missing or different from the version first published, and the speech in a "
    "video may drift out of step with the speaker's lip movements. Each problem erodes audience trust and conversion, "
    "yet none is reported by standard analytics dashboards.",
    "Advances in computer vision, speech processing and audio signal processing make it practical to detect several of "
    "these problems automatically. Optical character recognition (OCR), QR-code detection and speech recognition can "
    "recover web addresses that are shown or spoken in a video. Audio fingerprinting can compare a current audio track "
    "with a stored reference. Audio-visual synchronisation networks such as SyncNet learn whether a speaker's mouth "
    "movements correspond to the soundtrack. At the same time, creators must follow fast-changing platform features and "
    "content trends that are scattered across many news sources.",
    "AROHA (AI-Powered Social Media Analyzer) combines these capabilities in one publicly accessible web application. "
    "It integrates official Instagram analytics, a safe broken-link detector, an audio loss detector, an AI-based "
    "lip-sync mismatch detector and a news and trends module, built with Next.js, FastAPI, PostgreSQL and Python AI "
    "libraries. The initial scope is Instagram only, and the architecture is kept modular so that other platforms can "
    "be added later.",
]

PROBLEM = [
    "Instagram creators and businesses lack a single tool that combines account analytics with integrity checks on "
    "their multimedia content. Official analytics do not report broken promotional links, missing or replaced Reel "
    "audio, or audio-video synchronisation errors, and the Instagram API restricts which metrics are available, how "
    "long they are retained and which account types may connect. Research on audio fingerprinting and lip-sync "
    "detection has rarely been packaged for creators, nor evaluated on varied social-media-style video with confidence "
    "reporting and rejection of unsuitable input.",
    "This project develops AROHA, a platform that (i) retrieves and stores official Instagram metrics honestly, "
    "distinguishing API values from calculated estimates; (ii) detects problematic links, audio and synchronisation "
    "using explainable and measurable methods; and (iii) reports uncertainty instead of guessing when the evidence is "
    "insufficient.",
]

MOTIVATION = [
    "**Keeping creator content trustworthy.** A dead product link or a muted Reel is invisible in standard analytics, "
    "so the creator often learns about it only after lost sales or audience complaints. An automated checker gives "
    "early, evidence-based warnings.",
    "**Making analytics honest and durable.** Instagram's account insights are retained only for a limited period and "
    "do not identify who unfollowed. Storing daily snapshots and clearly separating API metrics from calculated "
    "estimates lets creators study long-term growth without misleading claims.",
    "**Bringing research methods to practical use.** Audio fingerprinting and audio-visual synchronisation are "
    "well-studied but are not available to ordinary creators in a usable, explainable form. Evaluating them on a "
    "labelled dataset, with measured accuracy and stated limits, also gives the project genuine research value for an "
    "MCA major project.",
    "**Protecting privacy and platform rules.** AROHA never asks for Instagram passwords, uses only Meta's official "
    "authorisation flow and treats uploaded media as private, which is a requirement for any tool that handles "
    "creators' accounts.",
]

LIT_INTRO = (
    "Thirteen works and sources were reviewed, covering social media analytics, the Instagram Platform, link rot, "
    "promotional content, text and speech recognition, audio fingerprinting, audio-visual synchronisation and "
    "facial landmark tracking. Each entry notes the approach and its limitation relative to AROHA."
)

LIT = [
    "Batrinca and Treleaven (2015) surveyed the techniques, tools and platforms used for social media analytics, "
    "covering data collection, text analytics and visualisation. However, the survey predates today's "
    "permission-based Instagram professional-account APIs and gives little guidance on multimedia integrity checks.",
    "Meta (2026) documents the Instagram Platform for Business and Creator accounts, including Instagram Login, the "
    "`instagram_business_basic` and `instagram_business_manage_insights` permissions, and the account and media "
    "insights endpoints. The documentation states that insights are available only for professional accounts, that "
    "account-level data is retained for a limited period (about 90 days), that some metrics are unavailable on small "
    "accounts and that data can lag. Long-term growth tracking therefore needs stored snapshots, and unsupported "
    "metrics must be labelled rather than invented.",
    "Klein et al. (2014) measured reference rot in scholarly articles and found that roughly one in five articles "
    "contained links that no longer led to the referenced content. However, the study concerns scholarly "
    "references, not promotional links on social media, and it provides no monitoring tool for creators.",
    "Mathur et al. (2018) studied affiliate marketing disclosures on YouTube and Pinterest by analysing the links and "
    "disclosures attached to posts. However, their analysis relies on text metadata. Links shown on screen, encoded in "
    "QR codes or spoken in a video are not examined, and link health is not checked.",
    "Baek et al. (2019) proposed CRAFT, which detects text by predicting character regions and the affinity between "
    "characters, and which underlies the detector of the EasyOCR library. However, it is trained for scene text, so "
    "compressed video frames, motion blur and stylised overlays can reduce accuracy, and extracted strings must be "
    "validated as real URLs.",
    "Radford et al. (2023) introduced Whisper, a speech recognition model trained on 680,000 hours of weakly "
    "supervised multilingual audio and shown to be robust to accents and noise. However, spoken web addresses mix "
    "letters, digits and punctuation and are inherently ambiguous, and transcripts of non-speech audio can be "
    "unreliable, so spoken URLs must be treated as candidates.",
    "Wang (2003) described the landmark-based audio search algorithm behind Shazam, which hashes pairs of spectrogram "
    "peaks and identifies a recording from the consistency of their time offsets, even in noise. However, it was "
    "designed to identify short music snippets in a large database rather than to verify one creator's own track "
    "against a stored reference.",
    "Haitsma and Kalker (2002) proposed a robust fingerprint of 32-bit sub-fingerprints derived from energy "
    "differences across frequency bands, compared using bit error rate. However, the method is sensitive to time "
    "scaling and pitch changes and is not designed to explain what kind of change occurred.",
    "Chung and Zisserman (2016) proposed SyncNet, a two-stream convolutional network that embeds a short mouth-region "
    "video clip and the corresponding audio into a shared space, allowing the audio-video offset to be estimated and "
    "lip-sync errors to be detected. However, it was trained on broadcast-style speaking faces, so profile views, "
    "occlusion, music and heavy editing can reduce reliability.",
    "Prajwal et al. (2020) used a pretrained lip-sync expert discriminator in Wav2Lip and introduced the LSE-D and "
    "LSE-C metrics (Lip Sync Error distance and confidence) derived from the SyncNet-style expert. However, these "
    "metrics were designed to score generated talking faces, not to diagnose ordinary uploaded videos or to report "
    "an offset in milliseconds with calibrated thresholds.",
    "Iashin et al. (2024) proposed Synchformer, which estimates audio-visual offsets in open-domain video using "
    "sparse cues and segment-level features. However, it is not specific to speech, needs substantial computing "
    "resources and treats offset estimation over a bounded range rather than explaining non-speech or "
    "creative-editing cases.",
    "Haliassos et al. (2021) showed that features learned from lip-reading help detect face forgeries and generalise "
    "to unseen manipulations, using mouth-movement inconsistencies as a cue. However, their goal is real-versus-fake "
    "classification, not routine synchronisation checking with an estimated offset for creators.",
    "Lugaresi et al. (2019) presented MediaPipe, a framework for real-time perception pipelines that includes face "
    "detection and facial landmark models. However, landmarks give mouth geometry only and do not by themselves "
    "establish correspondence with audio, so they must be paired with an audio-visual synchronisation method.",
]

REFS = [
    "[1] Batrinca, B., & Treleaven, P. (2015). Social media analytics: a survey of techniques, tools and platforms. "
    "AI & Society, 30(1), 89\u2013116.",
    "[2] Meta Platforms, Inc. (2026). Instagram Platform documentation: Instagram API with Instagram Login; Insights. "
    "Meta for Developers. https://developers.facebook.com/docs/instagram-platform (accessed 2 November 2026).",
    "[3] Klein, M., Van de Sompel, H., Sanderson, R., Shankar, H., Balakireva, L., Zhou, K., & Tobin, R. (2014). "
    "Scholarly context not found: one in five articles suffers from reference rot. PLoS ONE, 9(12), e115253.",
    "[4] Mathur, A., Narayanan, A., & Chetty, M. (2018). Endorsements on social media: an empirical study of affiliate "
    "marketing disclosures on YouTube and Pinterest. Proceedings of the ACM on Human-Computer Interaction, 2(CSCW), "
    "Article 119.",
    "[5] Baek, Y., Lee, B., Han, D., Yun, S., & Lee, H. (2019). Character region awareness for text detection. "
    "Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR).",
    "[6] Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). Robust speech "
    "recognition via large-scale weak supervision. Proceedings of the 40th International Conference on Machine "
    "Learning (ICML), PMLR 202.",
    "[7] Wang, A. (2003). An industrial-strength audio search algorithm. Proceedings of the 4th International "
    "Conference on Music Information Retrieval (ISMIR).",
    "[8] Haitsma, J., & Kalker, T. (2002). A highly robust audio fingerprinting system. Proceedings of the 3rd "
    "International Conference on Music Information Retrieval (ISMIR).",
    "[9] Chung, J. S., & Zisserman, A. (2016). Out of time: automated lip sync in the wild. Workshop on Multi-view "
    "Lip-reading, Asian Conference on Computer Vision (ACCV).",
    "[10] Prajwal, K. R., Mukhopadhyay, R., Namboodiri, V. P., & Jawahar, C. V. (2020). A lip sync expert is all you "
    "need for speech to lip generation in the wild. Proceedings of the 28th ACM International Conference on "
    "Multimedia.",
    "[11] Iashin, V., Xie, W., Rahtu, E., & Zisserman, A. (2024). Synchformer: efficient synchronization from sparse "
    "cues. IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP).",
    "[12] Haliassos, A., Vougioukas, K., Petridis, S., & Pantic, M. (2021). Lips don't lie: a generalisable and robust "
    "approach to face forgery detection. Proceedings of the IEEE/CVF CVPR.",
    "[13] Lugaresi, C., Tang, J., Nash, H., et al. (2019). MediaPipe: a framework for building perception pipelines. "
    "arXiv:1906.08172.",
    "[14] International Telecommunication Union Radiocommunication Sector (1998). Recommendation ITU-R BT.1359-1: "
    "Relative timing of sound and vision for broadcasting.",
]

GAPS = [
    ("No unified creator-facing platform",
     ["Analytics tools, link checkers, audio tools and lip-sync research exist separately, but no reviewed work "
      "combines Instagram analytics, promotional link monitoring, audio integrity, lip-sync analysis and trend "
      "discovery for creators.",
      "There is a need for one platform with a shared account system, job queue and reporting layer."]),
    ("Honest analytics under API restrictions",
     ["The Instagram API limits metrics, retention and eligible accounts, and does not identify individual "
      "unfollowers.",
      "Daily snapshot storage, documented formulas and explicit labels separating API metrics from calculated "
      "estimates are needed so that no unsupported claim is shown to the user."]),
    ("Link integrity in multimodal content",
     ["Links appear in captions, bios, on-screen text, QR codes and speech, but existing studies mostly examine "
      "text metadata.",
      "Safe validation is also required: a 403 response or a timeout is not proof that a link is broken, and "
      "fetching user-supplied URLs must be protected against server-side request forgery (SSRF)."]),
    ("Audio continuity checking for creators",
     ["Fingerprinting algorithms were designed mainly for music identification. Creators need a comparison of their "
      "own reference against a current file, with a clear distinction between a silent or missing track inside a "
      "video file and a licensed music track becoming unavailable on the platform.",
      "When no earlier reference exists, the system must say that the previous status cannot be verified."]),
    ("Lip-sync analysis on real social-media video",
     ["SyncNet-style models are evaluated mainly on speaking faces in broadcast-like material. Social videos include "
      "music, voice-over, dubbing, cuts and absent faces.",
      "A practical system must reject unsuitable input, estimate the offset in milliseconds with a confidence "
      "score, calibrate thresholds, and be evaluated on a labelled held-out set with a baseline comparison."]),
    ("Privacy-by-design and truthful evaluation",
     ["Retention of uploaded media and its use for model training should require separate, explicit consent.",
      "Reported accuracy must come from measured experiments on a documented dataset, not from assumed figures."]),
]

OBJECTIVES = [
    "Develop a public multi-user web platform with secure registration, login, per-user data isolation and Meta's "
    "official OAuth for eligible Creator and Business accounts, keeping tokens encrypted and on the backend only.",
    "Provide Instagram analytics that store daily snapshots and report follower growth, net follower change "
    "(daily, weekly, monthly) and engagement rate by documented formulas, labelling API metrics and calculated "
    "estimates separately.",
    "Build a link analyzer that extracts URLs from bios, captions, video frames (OCR), QR codes and speech, and "
    "validates them safely with SSRF protection into five statuses: Working, Broken, Redirected, Suspicious and "
    "Unverified.",
    "Build an audio loss detector using FFmpeg, librosa and acoustic fingerprinting that classifies audio into six "
    "categories and reports a similarity score against a stored reference.",
    "Build a lip-sync analyzer using a pretrained audio-visual synchronisation model and MediaPipe that estimates "
    "offset in milliseconds with a confidence score, and evaluate it on a held-out set of 100\u2013200 labelled clips "
    "using accuracy, precision, recall, F1-score, confusion matrix, ROC-AUC, offset MAE and processing time against "
    "a baseline.",
    "Collect Instagram and social media news from official, RSS and licensed API sources into a filterable trends "
    "module, and deliver the system with automated tests, documentation and a measured evaluation report.",
]

METHOD = [
    ("Requirement study and API feasibility check.",
     "Review Meta's current documentation for permissions, account eligibility, access levels (Standard and "
     "Advanced Access, App Review), available metrics and rate limits. For every feature that depends on an "
     "unavailable permission, define a fallback such as manual upload."),
    ("Foundation: database, backend and interface shell.",
     "Create the PostgreSQL schema with migrations, the modular FastAPI services, authentication using a modern "
     "password hash and secure sessions, and the Next.js shell with the AROHA logo, collapsible sidebar and landing "
     "page."),
    ("Instagram integration and analytics.",
     "Implement the Instagram Login OAuth flow with state validation, server-side token exchange, long-lived token "
     "renewal and encrypted storage. A scheduled job stores daily snapshots. Engagement rate by reach is "
     "(total interactions / reach) \u00d7 100 and by followers is (total interactions / followers) \u00d7 100; the "
     "two are never mixed in one chart. Net follower change is F(t) \u2212 F(t\u22121), aggregated weekly and monthly."),
    ("Broken promotional link analyzer.",
     "Sample video frames with OpenCV, read text with EasyOCR or PaddleOCR, decode QR codes with OpenCV's "
     "QRCodeDetector, transcribe speech with Whisper and extract URLs by pattern matching and normalisation. "
     "A phrase such as \u201clink in bio\u201d maps to the account's bio link and never to an invented URL. Rule-based "
     "classification flags promotional content first. Validation uses HTTPX with manual redirect handling: each hop "
     "is re-resolved and checked against private, loopback and link-local addresses, with timeouts and a response "
     "size limit."),
    ("Audio loss detector.",
     "Probe streams with FFprobe, extract mono audio with FFmpeg and detect missing streams and silence from "
     "signal level. Build a landmark fingerprint from STFT spectral peaks (SciPy, NumPy), match reference and "
     "current hashes by the consistency of their time offsets, and add librosa feature correlation as secondary "
     "evidence. Map results to the six categories, with \u201cUnable to verify\u201d when no reference exists."),
    ("Lip-sync analyzer.",
     "Validate uploads, resample video to a fixed frame rate and audio to 16 kHz, detect faces and crop the mouth "
     "region with MediaPipe, and detect speech activity. A pretrained SyncNet-style model (licence permitting) "
     "scores audio-video distance over a range of candidate offsets for each window. The offset is the minimum-"
     "distance shift and confidence is the gap between median and minimum distance. Initial thresholds follow the "
     "perceptual limits in ITU-R BT.1359-1 and are then calibrated on the evaluation set. A landmark-and-audio-"
     "envelope correlation serves as the baseline."),
    ("News and trends module.",
     "Run scheduled collectors for official announcements, RSS feeds and a licensed news API, with no "
     "unauthorised scraping. Normalise, deduplicate by URL, assign the ten categories using a keyword taxonomy and "
     "cache results with source metadata."),
    ("Evaluation, testing and documentation.",
     "Write unit, integration, system and security tests, run the lip-sync evaluation on the held-out set, record "
     "dataset composition, model version, environment and measured metrics, and prepare the project report, user "
     "manual and README."),
]

ARCH_TEXT = [
    "AROHA follows a four-layer architecture, shown in Figure 1. The **presentation layer** is a Next.js "
    "application (React, TypeScript, Tailwind CSS, Recharts) that provides the public landing page, authentication "
    "pages, a single shared layout with a collapsible sidebar, structured analytics dashboards and masonry grids for "
    "news and visual results. It communicates with the backend only through REST/JSON calls and multipart uploads.",
    "The **application layer** is a FastAPI service divided into routers and services for authentication, Instagram "
    "OAuth, analytics and follower history, link analysis, audio analysis, lip-sync analysis, news and reporting. "
    "Pydantic validates requests, SQLAlchemy accesses the database, and rate limiting, ownership checks and audit "
    "logging protect each endpoint. Instagram tokens are encrypted and never leave the backend.",
    "The **processing layer** runs expensive work outside normal requests. Requests for video or audio analysis "
    "create a job record and a Celery task through a Redis broker. Worker modules (link detector, audio detector, "
    "lip-sync detector) update job progress, which the interface polls. The **data layer** consists of PostgreSQL "
    "for users, encrypted connections, analytics history, media metadata, reports, news, jobs and consent records, "
    "and controlled media storage in which temporary files are deleted and uploads are retained only with explicit "
    "consent. External integrations are Meta's Instagram API and news sources.",
]

DATASETS = [
    ("Instagram analytics",
     "Live data from Meta's API for Creator/Business accounts that the user authorises (test accounts during "
     "development), plus daily snapshots stored by AROHA.",
     "Grows daily; no fixed size",
     "Dashboards and growth calculations"),
    ("Demo data",
     "Synthetic series generated by the team and always labelled \u201cDemo mode\u201d.",
     "Small, synthetic",
     "Demonstration and UI testing only"),
    ("Link analysis tests",
     "Controlled test server returning 200, 301/302, 403, 404, 500, slow and looping responses; public example "
     "domains; team-made videos with printed URLs, QR codes and spoken links.",
     "To be created (target: 50+ cases)",
     "Unit and system testing of extraction and validation"),
    ("Audio loss tests",
     "Self-recorded or openly licensed clips with synthetic changes made by FFmpeg (muted, removed track, replaced "
     "audio, truncated or dropped segments).",
     "To be created (target: 60+ cases)",
     "Accuracy of the six audio categories"),
    ("Lip-sync evaluation set",
     "Consented self-recordings and openly licensed speech-video corpora (for example, the GRID audiovisual "
     "corpus; licence to be confirmed before use). Offset clips are produced by shifting the audio by controlled "
     "amounts (for example \u00b140, \u00b180, \u00b1120, \u00b1200, \u00b1300 and \u00b1500 ms) so the true label is known. "
     "Non-speech clips are included for rejection testing.",
     "Target 100\u2013200 labelled clips; not yet collected",
     "Held-out evaluation, threshold calibration, baseline comparison"),
    ("News and trends",
     "Official announcements, RSS feeds and a licensed news API used within their terms.",
     "Refreshed on a schedule",
     "News cards, categories and trending topics"),
]

TECH = [
    "**Programming languages:** Python 3.11+ (backend and AI), TypeScript (frontend), SQL.",
    "**Frontend:** Next.js, React, Tailwind CSS, Recharts, Lucide React and a form-validation library.",
    "**Backend:** FastAPI, Pydantic, SQLAlchemy, Alembic, HTTPX, Celery.",
    "**AI and signal processing:** OpenCV, MediaPipe, PyTorch, librosa, NumPy, SciPy, FFmpeg, Whisper, EasyOCR or "
    "PaddleOCR, a pretrained SyncNet-style synchronisation model, scikit-learn for evaluation metrics.",
    "**Database and queue:** PostgreSQL and Redis.",
    "**Integrations:** Meta Instagram API (OAuth 2.0), RSS feeds and a licensed news API.",
    "**Tools and platform:** Git, VS Code or Zed, pytest, Postman, Docker (optional), Windows or Linux with an "
    "optional CUDA-capable GPU.",
]

OUTCOMES = [
    "A deployed, publicly accessible AROHA web application with registration, login, profile management and account "
    "deletion.",
    "Secure Instagram connection for eligible accounts and an analytics dashboard with stored history, growth "
    "charts and clearly labelled metrics.",
    "A link analyzer that reports Working, Broken, Redirected, Suspicious or Unverified links with evidence and "
    "exportable reports.",
    "An audio loss detector with fingerprint storage, history and a six-category report with similarity scores.",
    "A lip-sync analyzer that returns a synchronisation category, offset in milliseconds, confidence, problem "
    "timestamps and a waveform view.",
    "A research dataset module and an evaluation report containing measured accuracy, precision, recall, F1-score, "
    "confusion matrix, ROC-AUC, offset error and processing time against a baseline.",
    "A news and trends module with filters, search and links to original articles.",
    "Project documentation: SRS, design diagrams, test cases, user manual, README and final report.",
]

NOVELTY = [
    "AROHA is the only reviewed approach that unifies Instagram analytics, multimodal link integrity, audio "
    "continuity and lip-sync analysis, and creator-oriented trend discovery in one consent-aware platform.",
    "It treats uncertainty as a first-class result. Every module can answer \u201cunable to verify\u201d or "
    "\u201cinsufficient data\u201d, and analytics labels API-provided values separately from calculated estimates.",
    "Its link checker covers links shown on screen, encoded in QR codes and spoken in video, and avoids false "
    "alarms by treating 403 responses and timeouts as Unverified rather than Broken.",
    "Its lip-sync module reports an offset in milliseconds with calibrated thresholds, rejects non-speech or "
    "faceless clips, and is evaluated against a baseline on a documented labelled set, with every figure measured "
    "rather than assumed.",
]

LIMITS = [
    "Instagram data is available only for Creator and Business accounts. Personal accounts cannot be connected, "
    "although they can use the upload-based features.",
    "Serving other people's accounts publicly requires Meta's Advanced Access, which involves App Review and "
    "business verification. Development will use accounts owned by the team.",
    "Instagram does not identify individual unfollowers, and account insights are retained for a limited period, so "
    "only net changes from stored snapshots can be shown. Metric availability may change as Meta updates its API.",
    "Instagram licensed-music removal on the platform cannot be assumed to be exposed by the API. AROHA detects "
    "silence, absence or change in the files it can access.",
    "Lip-sync results depend on a visible, frontal speaking face. Music videos, dubbing, voice-over and creative "
    "editing can legitimately look unsynchronised and are reported as uncertain, not as errors.",
    "The evaluation set will be small (100\u2013200 clips), so reported accuracy will describe that set and may not "
    "generalise to all videos. Computing resources limit the length and number of videos processed.",
]

FUTURE = [
    "Add other platforms (YouTube, Facebook, TikTok, X) behind the modular integration layer.",
    "Train a promotional-content classifier once enough labelled examples are available.",
    "Fine-tune a synchronisation model on a larger, appropriately licensed dataset.",
    "Add scheduled monitoring, e-mail alerts and team accounts for agencies.",
]


# --------------------------------------------------------------------------- build
def fill_toc_table(doc, builder):
    t = doc.tables[0]
    keys = [k for k, _, _ in TOC]
    for i, (key, name, desc) in enumerate(TOC, start=1):
        row = t.rows[i]
        for ci in range(4):
            cell = row.cells[ci]
            for p in cell.paragraphs[1:]:
                p._p.getparent().remove(p._p)
            p = cell.paragraphs[0]
            for r in list(p.runs):
                r._r.getparent().remove(r._r)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci in (0, 3) else WD_ALIGN_PARAGRAPH.LEFT
            if ci == 0:
                r = p.add_run(str(i))
                style_run(r, 12)
            elif ci == 1:
                r = p.add_run(name)
                style_run(r, 12, True)
            elif ci == 2:
                r = p.add_run(desc)
                style_run(r, 11)
            else:
                add_field(p, f"PAGEREF _Toc_{key} \\h", "1", size=12)
    # header row text tidy-up
    for cell, txt in zip(t.rows[0].cells, ["Sl. No.", "Section", "Description", "Page No."]):
        p = cell.paragraphs[0]
        for r in list(p.runs):
            r._r.getparent().remove(r._r)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(txt)
        style_run(r, 12, True)


def add_footer_page_number(doc):
    sec = doc.sections[0]
    footer = sec.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(p, "PAGE", "1", size=11)


def main():
    shutil.copy(TEMPLATE, os.path.join(HERE, "_synopsis_template_copy.docx"))
    doc = docx.Document(os.path.join(HERE, "_synopsis_template_copy.docx"))
    paras = doc.paragraphs

    # cover page fields
    set_paragraph_text(paras[2], USN)
    set_paragraph_text(paras[4], TITLE)
    paras[4].runs[0].font.size = Pt(16)
    set_paragraph_text(paras[9], f"{STUDENT}\n{USN}")
    set_paragraph_text(paras[15], GUIDE)
    set_paragraph_text(paras[16], DESIG)

    fill_toc_table(doc, None)
    trim_body(doc, 30)  # keep cover page, TOC heading and TOC table

    b = Builder(doc, line_spacing=1.5, base_size=12, toc_prefix="_Toc")

    def H(num, text, key, level=1, page_break=False):
        b.heading(f"{num}.  {text}", level, key=key, center=False, page_break=page_break)

    H(1, "Title", "title", page_break=True)
    b.para(TITLE, align="center", bold=True, size=13)

    H(2, "Introduction / Background", "intro")
    for t in INTRO:
        b.para(t)

    H(3, "Problem Statement", "problem")
    for t in PROBLEM:
        b.para(t)

    H(4, "Motivation", "motivation")
    for t in MOTIVATION:
        b.para(t)

    H(5, "Literature Survey", "lit")
    b.para(LIT_INTRO)
    b.numbered([f"{x.replace('`', '')} [{i}]" for i, x in enumerate(LIT, 1)], after=4, left_cm=0.9, hang_cm=0.9)

    H(6, "Research / Technical Gap", "gap")
    b.para("Based on the literature survey, the following gaps motivate the proposed project.")
    for i, (title, lines) in enumerate(GAPS, 1):
        b.para(f"**{i}. {title}**", align="left", after=2, keep_next=True)
        b.bullets(lines, after=2)

    H(7, "Objectives", "objectives")
    b.para("The project has six specific and measurable objectives.")
    b.numbered(OBJECTIVES, after=4, left_cm=0.9, hang_cm=0.9)

    H(8, "Proposed Methodology", "method")
    b.para("The work will be carried out in the following eight steps.")
    for i, (head, body) in enumerate(METHOD, 1):
        b.para(f"**Step {i}: {head}** {body}", after=5)

    H(9, "Proposed System / Architecture", "arch")
    for t in ARCH_TEXT:
        b.para(t)
    b.figure(os.path.join(IMG, "architecture.png"), 12.6, ("1", "Layered architecture of AROHA"))

    H(10, "Dataset / Data Sources", "dataset")
    b.para("AROHA uses live platform data, controlled test data and a purpose-built evaluation dataset. No dataset "
           "has been collected yet; the sizes below are targets, and only publicly licensed, appropriately licensed "
           "or consented material will be used. Private user videos and Instagram data will not be used for model "
           "training without separate, explicit consent.")
    b.table(["Data", "Source and description", "Size / status", "Use"],
            [list(r) for r in DATASETS], [2.6, 7.2, 3.3, 3.9], size=10, caption=("1", "Data sources and datasets"),
            bold_first_col=True)

    H(11, "Technology Stack", "tech")
    b.bullets(TECH, after=3)

    H(12, "Expected Outcomes", "outcomes")
    b.para("At completion the project is expected to deliver the following.")
    b.bullets(OUTCOMES, after=3)

    H(13, "Innovation / Novelty", "novelty")
    b.bullets(NOVELTY, after=4)

    H(14, "Limitations / Future Work", "limits")
    b.para("**Limitations:**", align="left", after=2, keep_next=True)
    b.bullets(LIMITS, after=3)
    b.para("**Future work:**", align="left", after=2, keep_next=True)
    b.bullets(FUTURE, after=3)

    H(15, "References", "refs")
    for r in REFS:
        p = b.para("", align="left", after=4, left_cm=1.0, first_cm=-1.0, line=1.2)
        add_marked_runs(p, r, 11)

    b.para("", after=14)
    b.para("Signature of the Student:", align="left", after=4)
    b.para("Date:", align="left", after=4)

    # bookmarks for TOC rows that have no heading of their own are handled via headings above
    add_footer_page_number(doc)
    enable_update_fields_on_open(doc)
    out = os.path.abspath(OUT)
    doc.save(out)
    os.remove(os.path.join(HERE, "_synopsis_template_copy.docx"))
    print("saved", out)


if __name__ == "__main__":
    main()
