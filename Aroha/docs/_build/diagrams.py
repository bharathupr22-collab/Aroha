"""Generates the architecture, DFD, use-case and ER diagrams used in the AROHA documents.

Run:  python diagrams.py
Output: ./img/*.png
"""
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle, FancyArrowPatch, Circle

NAVY = "#17212B"
IVORY = "#F7F8F5"
TEAL = "#2A9D8F"
LAV = "#A78BFA"
AMBER = "#E9B44C"
SLATE = "#475569"
WHITE = "#FFFFFF"
TEAL_L = "#D5EEEA"
LAV_L = "#E9E3FD"
AMBER_L = "#FAF0D5"
GREY_L = "#E8ECEF"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


def canvas(w, h, xmax, ymax, xmin=0):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    return fig, ax


def box(ax, x, y, w, h, text, fc=WHITE, ec=NAVY, fs=8, tc=NAVY, bold=False, lw=1.2, r=1.2):
    """Rounded box with its centre at (x, y)."""
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=fc, ec=ec, lw=lw)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(ax, p1, p2, text=None, both=False, color=NAVY, fs=7, rad=0.0, off=(0, 0), lw=1.1, ls="-", head=True):
    style = "<|-|>" if both else ("-|>" if head else "-")
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=9, lw=lw,
                        color=color, connectionstyle=f"arc3,rad={rad}", linestyle=ls, shrinkA=0, shrinkB=0)
    ax.add_patch(a)
    if text:
        mx, my = (p1[0] + p2[0]) / 2 + off[0], (p1[1] + p2[1]) / 2 + off[1]
        ax.text(mx, my, text, ha="center", va="center", fontsize=fs, color=SLATE,
                bbox=dict(fc=WHITE, ec="none", pad=0.8), linespacing=1.2)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=220, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)


# --------------------------------------------------------------------------- architecture
def architecture():
    fig, ax = canvas(8, 8.6, 100, 108)
    for (y0, y1, label, col) in [
        (92, 107, "PRESENTATION LAYER", TEAL_L),
        (70, 88, "APPLICATION / API LAYER", LAV_L),
        (38, 62, "ASYNCHRONOUS PROCESSING & AI LAYER", AMBER_L),
        (2, 30, "DATA & EXTERNAL SERVICES LAYER", GREY_L),
    ]:
        ax.add_patch(Rectangle((1, y0), 98, y1 - y0, fc=col, ec=NAVY, lw=0.8))
        ax.text(2.5, y1 - 1.8, label, fontsize=7, fontweight="bold", color=NAVY, va="center")

    box(ax, 50, 98, 92, 8.5, "Next.js (React, TypeScript)  |  Tailwind CSS  |  Recharts  |  Lucide Icons\n"
        "Landing page, auth pages, collapsible sidebar, dashboards, masonry news grid, upload UI",
        fs=7.3)

    arrow(ax, (50, 93.7), (50, 86), "HTTPS / REST (JSON, multipart upload)", both=True, fs=6.8)

    names = ["Auth", "Instagram\nOAuth", "Analytics", "Link\nAnalyzer", "Audio\nDetector", "Lip-Sync", "News"]
    xs = [9.5, 22.5, 36, 50, 64, 77.5, 90.5]
    for n, x in zip(names, xs):
        box(ax, x, 79.5, 12, 7, n, fs=6.8)
    ax.text(50, 72.4, "FastAPI routers | Pydantic validation | SQLAlchemy ORM | JWT / secure session | rate limiting | audit log",
            ha="center", va="center", fontsize=6.0, color=SLATE)

    # enqueue arrow lands on the Redis box
    arrow(ax, (14, 70), (14, 56), both=True)
    ax.text(15.5, 65.5, "enqueue job /\npoll status", fontsize=6.3, color=SLATE, va="center", linespacing=1.2)

    box(ax, 14, 48, 17, 15, "Redis\n(message broker)\n+\nCelery workers", fs=6.8)
    box(ax, 40, 48, 22, 17, "Link Detector\nOpenCV frames, QR\nEasyOCR, Whisper\nURL extraction\nSafe HTTP validation", fs=6.5)
    box(ax, 65, 48, 22, 17, "Audio Detector\nFFmpeg extraction\nlibrosa features\nFingerprinting\nSimilarity scoring", fs=6.5)
    box(ax, 87.5, 48, 14, 17, "Lip-Sync\nDetector\nMediaPipe faces\nPyTorch\nSyncNet-style\nA/V offset", fs=6.2)
    arrow(ax, (22.5, 48), (29, 48), both=True)

    box(ax, 14, 14, 24, 14, "PostgreSQL\nusers, accounts (encrypted\ntokens), analytics history,\nmedia, reports, news, jobs,\nconsent records", fs=6.3)
    box(ax, 40, 14, 20, 14, "Media storage\n(validated uploads;\ntemporary files cleaned;\nretained only with\nconsent)", fs=6.3)
    box(ax, 78, 14, 18, 14, "Meta Instagram\nGraph API\n(OAuth 2.0, insights,\nmedia metadata)", fs=6.3, ec=TEAL, lw=1.6)
    box(ax, 93.5, 14, 11, 14, "News API\n/ RSS\nfeeds", fs=6.3, ec=TEAL, lw=1.6)

    # data bus from workers
    for x in (40, 65, 87.5):
        ax.plot([x, x], [39.5, 34], color=SLATE, lw=1.0)
    ax.plot([14, 87.5], [34, 34], color=SLATE, lw=1.0)
    arrow(ax, (14, 34), (14, 21), color=SLATE, lw=1.0)
    arrow(ax, (40, 34), (40, 21), color=SLATE, lw=1.0)
    ax.text(52, 35.8, "read / write results and files", fontsize=6, color=SLATE, ha="center",
            bbox=dict(fc=AMBER_L, ec="none", pad=0.5))

    # external integrations leave from API layer through the gaps between worker boxes
    arrow(ax, (78, 70), (78, 21), None, both=True, color=TEAL)
    ax.text(76.6, 65.5, "Graph API calls\n(HTTPS)", fontsize=6.2, color=SLATE, ha="right", va="center", linespacing=1.2)
    arrow(ax, (96, 70), (96, 21), None, both=True, color=TEAL)
    save(fig, "architecture.png")


# --------------------------------------------------------------------------- DFD level 0
def dfd0():
    fig, ax = canvas(7.6, 5.8, 100, 78)
    ax.add_patch(Circle((50, 40), 14, fc=TEAL_L, ec=NAVY, lw=1.4))
    ax.text(50, 40, "AROHA\nAI-Powered Social\nMedia Analyzer\n(Process 0)", ha="center", va="center",
            fontsize=8, fontweight="bold", color=NAVY, linespacing=1.3)
    box(ax, 11, 40, 20, 11, "User\n(registered /\nIG professional)", fs=7.2)
    box(ax, 89, 68, 20, 9, "Meta Instagram\nGraph API", fs=7.3)
    box(ax, 89, 40, 20, 9, "News sources\n(RSS / News API)", fs=7.3)
    box(ax, 89, 12, 20, 9, "Email service\n(SMTP)", fs=7.3)
    box(ax, 50, 8, 26, 8, "Researcher / Admin", fs=7.3)

    arrow(ax, (21, 44), (36, 44), "credentials, uploads,\nURLs, date filters", fs=6.3, off=(0, 4.5))
    arrow(ax, (36, 36), (21, 36), "dashboards, reports,\nstatus, news", fs=6.3, off=(0, -4.5))
    arrow(ax, (60, 50), (79, 66), "authorisation request,\ntoken exchange, insight calls", fs=6.2, off=(-8, 6.5), rad=-0.05)
    arrow(ax, (79, 63), (62.5, 48.5), "account data, metrics,\nmedia metadata", fs=6.2, off=(13, 1.5), rad=-0.05)
    arrow(ax, (79, 40), (64, 40), "article feeds", fs=6.3, off=(0, 3))
    arrow(ax, (60, 30), (79, 14.5), "password-reset e-mail", fs=6.3, off=(-3, -5.5))
    arrow(ax, (50, 12), (50, 26), "datasets, annotations,\nevaluation requests", fs=6.3, off=(-17, 0))
    save(fig, "dfd_level0.png")


# --------------------------------------------------------------------------- DFD level 1
def dfd1():
    fig, ax = canvas(8, 9.4, 100, 110)

    def proc(y, n, t):
        ax.add_patch(Circle((38, y), 6.8, fc=TEAL_L, ec=NAVY, lw=1.2))
        ax.text(38, y, f"{n}\n{t}", ha="center", va="center", fontsize=6.2, fontweight="bold", color=NAVY, linespacing=1.15)

    def store(x, y, name, w=28):
        ax.plot([x - w / 2, x + w / 2], [y + 3, y + 3], color=NAVY, lw=1.3)
        ax.plot([x - w / 2, x + w / 2], [y - 3, y - 3], color=NAVY, lw=1.3)
        ax.text(x, y, name, ha="center", va="center", fontsize=6.3, color=NAVY, linespacing=1.15)

    rows = {"1.0": 101, "2.0": 85.5, "3.0": 70, "4.0": 54.5, "5.0": 39, "6.0": 23.5, "7.0": 8}
    proc(rows["1.0"], "1.0", "Authenticate\n& manage users")
    proc(rows["2.0"], "2.0", "Connect\nInstagram")
    proc(rows["3.0"], "3.0", "Sync & analyse\nmetrics")
    proc(rows["4.0"], "4.0", "Analyse\nlinks")
    proc(rows["5.0"], "5.0", "Detect\naudio loss")
    proc(rows["6.0"], "6.0", "Analyse\nlip-sync")
    proc(rows["7.0"], "7.0", "Collect &\nserve news")

    box(ax, 8, 54.5, 13, 9, "User", fs=7.5)
    box(ax, 8, 90, 13, 9, "Meta\nGraph API", fs=7)
    box(ax, 8, 8, 13, 9, "News\nsources", fs=7)

    store(78, 101, "D1  Users & consent")
    store(78, 77.5, "D2  Accounts, tokens &\nanalytics history")
    store(78, 46.5, "D3  Media, fingerprints\n& reports")
    store(78, 23.5, "D4  Jobs & lip-sync results")
    store(78, 8, "D5  News articles")

    # user <-> processes
    for key in ["1.0", "3.0", "4.0", "5.0", "6.0", "7.0"]:
        y = rows[key]
        arrow(ax, (14.5, 54.5 + (y - 54.5) * 0.15), (31.6, y), None, both=True, color=SLATE, lw=0.9)
    ax.text(24.5, 63.5, "requests,\nuploads,\nresults", fontsize=6, color=SLATE, ha="center", bbox=dict(fc=WHITE, ec="none", pad=0.5))

    # Meta <-> 2.0, 3.0
    arrow(ax, (14.5, 90), (31.4, 86.5), "OAuth", both=True, fs=6, off=(-2, 3))
    arrow(ax, (14.5, 87), (32.5, 74.5), "insights", both=True, fs=6, off=(-6, 3))
    # news -> 7.0
    arrow(ax, (14.5, 8), (31.2, 8), "feeds", fs=6, off=(0, 2.4))

    # processes <-> stores
    arrow(ax, (44.8, 101), (64, 101), None, both=True, color=SLATE, lw=0.9)
    arrow(ax, (44.8, 85.5), (64, 79), "tokens (encrypted)", both=True, fs=5.8, color=SLATE, lw=0.9, off=(0, 2.4))
    arrow(ax, (44.8, 70), (64, 76), "snapshots, metrics", both=True, fs=5.8, color=SLATE, lw=0.9, off=(0, -2.6))
    arrow(ax, (44.8, 54.5), (64, 48.5), None, both=True, color=SLATE, lw=0.9)
    arrow(ax, (44.8, 39), (64, 44.5), None, both=True, color=SLATE, lw=0.9)
    arrow(ax, (44.8, 23.5), (64, 23.5), None, both=True, color=SLATE, lw=0.9)
    arrow(ax, (44.8, 8), (64, 8), None, both=True, color=SLATE, lw=0.9)
    save(fig, "dfd_level1.png")


# --------------------------------------------------------------------------- use case
def usecase():
    fig, ax = canvas(8, 8.4, 100, 104)
    ax.add_patch(Rectangle((24, 2), 54, 100, fc=IVORY, ec=NAVY, lw=1.3))
    ax.text(51, 99, "AROHA System", ha="center", fontsize=9, fontweight="bold", color=NAVY)

    def actor(x, y, label):
        ax.add_patch(Circle((x, y + 4), 1.8, fc=WHITE, ec=NAVY, lw=1.2))
        ax.plot([x, x], [y + 2.2, y - 3], color=NAVY, lw=1.2)
        ax.plot([x - 3, x + 3], [y + 0.5, y + 0.5], color=NAVY, lw=1.2)
        ax.plot([x, x - 2.6], [y - 3, y - 8], color=NAVY, lw=1.2)
        ax.plot([x, x + 2.6], [y - 3, y - 8], color=NAVY, lw=1.2)
        ax.text(x, y - 11, label, ha="center", va="top", fontsize=7, color=NAVY, linespacing=1.2)

    def uc(x, y, text, fc=TEAL_L):
        ax.add_patch(Ellipse((x, y), 24, 6.6, fc=fc, ec=NAVY, lw=1))
        ax.text(x, y, text, ha="center", va="center", fontsize=6.3, color=NAVY, linespacing=1.15)
        return (x, y)

    left = [
        (38, 93, "Register / Login /\nReset password"),
        (38, 84, "Manage profile /\nDelete account"),
        (38, 75, "Read news & trends"),
        (38, 66, "Check links manually"),
        (38, 57, "Upload reference &\nanalyse audio loss"),
        (38, 48, "Upload video &\nanalyse lip-sync"),
        (38, 39, "View / export reports"),
    ]
    right = [
        (65, 86, "Connect Instagram\n(OAuth)"),
        (65, 77, "View analytics\ndashboard"),
        (65, 68, "View unfollowers &\ngrowth analysis"),
        (65, 59, "Extract links from\nbio / captions"),
        (65, 50, "Disconnect Instagram"),
    ]
    res = [
        (38, 23, "Manage research\ndatasets"),
        (38, 14, "Evaluate lip-sync\nmodel"),
    ]
    pts_l = [uc(x, y, t) for x, y, t in left]
    pts_r = [uc(x, y, t, LAV_L) for x, y, t in right]
    pts_s = [uc(x, y, t, AMBER_L) for x, y, t in res]

    actor(9, 66, "Registered User")
    actor(91, 78, "Instagram\nProfessional User")
    ax.text(91, 56.5, "(is also a\nRegistered User)", ha="center", va="top", fontsize=6, color=SLATE)
    actor(91, 26, "Meta Platform\n(Instagram API)")
    actor(9, 22, "Researcher /\nAdmin")

    for (x, y) in pts_l:
        ax.plot([12, x - 12], [64, y], color=SLATE, lw=0.7)
    for (x, y) in pts_r:
        ax.plot([88, x + 12], [76, y], color=SLATE, lw=0.7)
    for i in (0, 1, 3):
        x, y = pts_r[i]
        ax.plot([88, x + 12], [25, y], color=TEAL, lw=0.7, ls="--")
    for (x, y) in pts_s:
        ax.plot([12, x - 12], [20, y], color=SLATE, lw=0.7)
    save(fig, "usecase.png")


# --------------------------------------------------------------------------- ER diagram
ENTITIES = {
    "users": ["PK id", "name", "email (unique)", "password_hash", "created_at", "updated_at"],
    "consent_records": ["PK id", "FK user_id", "consent_type", "consent_status", "recorded_at", "withdrawn_at"],
    "background_jobs": ["PK id", "FK user_id", "job_type", "job_status", "progress", "created_at", "completed_at"],
    "lipsync_analysis": ["PK id", "FK user_id", "video_reference", "synchronization_status", "estimated_offset_ms", "confidence_score", "analysis_report", "created_at"],
    "media_items": ["PK id", "FK user_id", "platform_media_id", "media_type", "media_reference", "caption", "created_at"],
    "connected_accounts": ["PK id", "FK user_id", "platform", "platform_user_id", "username", "encrypted_access_token", "token_expiry", "connection_status"],
    "news_articles": ["PK id", "title", "description", "source", "article_url (unique)", "category", "published_at", "fetched_at"],
    "link_analysis": ["PK id", "FK user_id", "FK media_id", "detected_url", "response_status", "validation_result", "issue_description", "checked_at"],
    "audio_references": ["PK id", "FK user_id", "FK media_id", "audio_fingerprint", "reference_file", "created_at"],
    "audio_analysis": ["PK id", "FK user_id", "FK media_id", "detected_status", "similarity_score", "analysis_date"],
    "analytics_history": ["PK id", "FK account_id", "metric_name", "metric_value", "reporting_period", "captured_at", "source", "calculation_method"],
}


def er():
    fig, ax = canvas(7.8, 9.0, 101, 118, xmin=-1)
    W = 19.0
    LH = 3.0
    # top-aligned layout: (centre x, top y)
    pos = {
        "users": (50.5, 116),
        "consent_records": (9.5, 82), "background_jobs": (30, 82), "lipsync_analysis": (50.5, 82),
        "media_items": (70.5, 82), "connected_accounts": (91, 82),
        "news_articles": (9.5, 38), "link_analysis": (30, 38), "audio_references": (50.5, 38),
        "audio_analysis": (70.5, 38), "analytics_history": (91, 38),
    }
    dims = {}
    for name, (x, ytop) in pos.items():
        attrs = ENTITIES[name]
        h = 5.0 + LH * len(attrs) + 1
        yc = ytop - h / 2
        dims[name] = (x, yc, W, h)
        ax.add_patch(Rectangle((x - W / 2, ytop - h), W, h, fc=WHITE, ec=NAVY, lw=1.1))
        ax.add_patch(Rectangle((x - W / 2, ytop - 5), W, 5, fc=NAVY, ec=NAVY))
        ax.text(x, ytop - 2.5, name, ha="center", va="center", fontsize=6.0, color="white", fontweight="bold")
        for i, a in enumerate(attrs):
            if a.startswith("PK"):
                col, wt = "#B8861B", "bold"
            elif a.startswith("FK"):
                col, wt = TEAL, "bold"
            else:
                col, wt = NAVY, "normal"
            ax.text(x - W / 2 + 0.9, ytop - 5 - 2.2 - LH * i, a, ha="left", va="center", fontsize=5.2, color=col, fontweight=wt)

    def top(n): x, y, w, h = dims[n]; return (x, y + h / 2)
    def bot(n): x, y, w, h = dims[n]; return (x, y - h / 2)

    def rel(parent, child, y_mid=None):
        p, c = bot(parent), top(child)
        ym = y_mid if y_mid is not None else (p[1] + c[1]) / 2
        ax.plot([p[0], p[0], c[0], c[0]], [p[1], ym, ym, c[1]], color=SLATE, lw=0.9)
        ax.text(c[0] + 1.2, c[1] + 1.8, "N", fontsize=6.3, color=NAVY, fontweight="bold", ha="left")

    users_bottom = bot("users")
    for ch in ["consent_records", "background_jobs", "lipsync_analysis", "media_items", "connected_accounts"]:
        rel("users", ch, y_mid=users_bottom[1] - 5)
    ax.text(users_bottom[0] - 2.2, users_bottom[1] - 2.4, "1", fontsize=6.3, color=NAVY, fontweight="bold", ha="left")
    mb = bot("media_items")
    for ch in ["link_analysis", "audio_references", "audio_analysis"]:
        rel("media_items", ch, y_mid=mb[1] - 5)
    ax.text(mb[0] + 1.2, mb[1] - 2.4, "1", fontsize=6.3, color=NAVY, fontweight="bold", ha="left")
    rel("connected_accounts", "analytics_history")
    cb = bot("connected_accounts")
    ax.text(cb[0] + 1.2, cb[1] - 2.4, "1", fontsize=6.3, color=NAVY, fontweight="bold", ha="left")

    ax.text(2, 3.5, "news_articles is independent of users: it is a shared,\ncached store of articles fetched from RSS feeds / news APIs.", fontsize=6, color=SLATE, va="center")
    ax.text(62, 3.5, "PK = primary key,  FK = foreign key,  1 : N = one-to-many", fontsize=6.3, color=SLATE, va="center")
    save(fig, "er_diagram.png")


if __name__ == "__main__":
    architecture()
    dfd0()
    dfd1()
    usecase()
    er()
    print("diagrams written to", OUT)
