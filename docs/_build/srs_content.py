"""Content (data only) for the AROHA SRS. Requirement IDs are assigned automatically by build_srs.py."""

H, M, L = "High", "Medium", "Low"

TITLE = "AROHA: AI-Powered Social Media Analyzer"
SUBTITLE = "An AI-Assisted Instagram Analytics and Multimedia Content Integrity Monitoring Platform"

# --------------------------------------------------------------------------- 1. Introduction
PURPOSE = (
    "This Software Requirements Specification (SRS) describes the requirements of **AROHA \u2013 AI-Powered Social Media "
    "Analyzer**, a public web application that combines Instagram analytics, broken promotional link detection, Reel "
    "audio loss detection, AI-based lip-sync mismatch detection, and social media news and trend discovery. It states "
    "what the system must do and the qualities it must have. It is intended for the project guide, the evaluators, "
    "and the developers and testers who will build and verify the system. The document follows the structure "
    "recommended by IEEE Std 830-1998 and ISO/IEC/IEEE 29148:2018."
)

SCOPE = [
    "Creators and businesses depend on Instagram to promote products and reach audiences, but official analytics do "
    "not show whether promotional links still work, whether Reel audio has gone missing or changed, or whether speech "
    "and lip movements are synchronised. AROHA brings these checks together with account analytics and a curated "
    "news feed in one place.",
    "AROHA will let any visitor register and use the features that do not need Instagram data (news, manual link "
    "checks, audio analysis with supplied files and lip-sync analysis of uploaded videos). Owners of eligible Instagram "
    "Creator or Business accounts can additionally connect through Meta's official authorisation flow to see follower "
    "growth, engagement analytics and account-linked link checks. The first version supports **Instagram only**; the "
    "design stays modular so other platforms can be added later.",
    "**Out of scope:** YouTube, Facebook, TikTok and X integrations; publishing content or sending messages on "
    "Instagram; collecting Instagram passwords or cookies, or automating Instagram login; identifying the usernames "
    "of people who unfollowed an account; unauthorised scraping; and training models on users' private data without "
    "their separate, explicit consent.",
]

DEFINITIONS = [
    ("AROHA", "The AI-Powered Social Media Analyzer web application described in this document."),
    ("Instagram professional account", "An Instagram Business or Creator account. Meta's Instagram Platform APIs serve "
     "these account types, not personal accounts."),
    ("Meta Graph API", "Meta's HTTP API through which authorised applications read Instagram account and media data."),
    ("OAuth 2.0", "The authorisation framework used to let a user grant AROHA limited access without sharing a password."),
    ("Access token", "A credential issued by Meta that lets AROHA call the Instagram API for one account."),
    ("Insights", "Instagram's account-level and media-level performance metrics (for example reach, views, interactions)."),
    ("Engagement rate", "Total interactions divided by a stated base (reach or followers) multiplied by 100. The base is "
     "always shown."),
    ("Net follower change", "Follower count at the end of a period minus the count at its start, calculated from stored "
     "snapshots."),
    ("SSRF", "Server-Side Request Forgery: an attack that makes a server request internal or unintended addresses."),
    ("OCR", "Optical Character Recognition: reading text from images or video frames."),
    ("ASR", "Automatic Speech Recognition: converting speech to text (Whisper is planned)."),
    ("Audio fingerprint", "A compact representation of audio content that allows two recordings to be compared."),
    ("Lip-sync", "The temporal alignment between a speaker's mouth movements and the speech audio."),
    ("A/V offset", "The time difference in milliseconds between audio and video. By convention in AROHA a positive value "
     "means the audio is ahead of the video."),
    ("SyncNet", "A pretrained audio-visual network that judges whether audio matches a speaker's mouth region."),
    ("MediaPipe", "A library providing face detection and facial landmark models."),
    ("FFmpeg / FFprobe", "Command-line tools for decoding, converting and inspecting audio and video."),
    ("Celery / Redis", "A task queue and message broker used to run heavy analyses in background workers."),
    ("JWT", "JSON Web Token: a signed token format that can carry session information."),
    ("CSRF", "Cross-Site Request Forgery: an attack that makes a browser send unwanted authenticated requests."),
    ("RSS", "Really Simple Syndication: a standard feed format for publishing news items."),
    ("Demo mode", "A clearly labelled mode that uses separate, synthetic data for demonstration."),
]

OVERVIEW = (
    "Section 2 gives the overall description of the product. Section 3 lists the system features and numbered "
    "functional requirements. Section 4 describes external interfaces. Section 5 gives the non-functional "
    "requirements. Section 6 presents the data flow, architecture and use case models. Section 7 describes the data "
    "requirements and database design. Section 8 lists constraints and limitations. Section 9 describes testing and "
    "acceptance criteria. Section 10 maps objectives to requirements, modules and test cases. Section 11 lists "
    "references."
)

# --------------------------------------------------------------------------- 2. Overall description
PERSPECTIVE = [
    "AROHA is a new, self-contained web application. It has three main parts: a **web client** (Next.js) used in the "
    "browser, a **backend** (FastAPI with background workers) that holds all business logic, secrets and AI "
    "pipelines, and a **data layer** (PostgreSQL and controlled media storage). The backend talks to Meta's "
    "Instagram API, to news sources (RSS feeds and a news API) and to an e-mail service for password recovery. The "
    "layered architecture is shown in Figure 6.3.",
    "Public website access and Instagram API eligibility are separate. Anyone can register and use the "
    "features that need no Instagram data; connected-account features depend on the account type, granted "
    "permissions and the data Meta actually provides.",
]

FUNCTIONS = [
    "Register, authenticate and manage private user accounts.",
    "Connect and disconnect an eligible Instagram Creator or Business account through Meta's official authorisation.",
    "Store daily follower and engagement snapshots and show growth, unfollow-related and engagement analytics.",
    "Extract and safely validate promotional links from bios, captions, video text, QR codes and speech.",
    "Fingerprint reference audio and detect missing, silent, changed or replaced audio.",
    "Analyse audio-video synchronisation of uploaded videos and estimate the offset in milliseconds.",
    "Collect, categorise and present social media news and trends from official, RSS and API sources.",
    "Run heavy analyses as background jobs and produce viewable, exportable reports.",
    "Manage user consent for media retention and model training, and manage research datasets and evaluations.",
]

USER_CLASSES = [
    ("Visitor", "Unauthenticated person who views the public landing page and registers.", "Basic"),
    ("Registered user (no Instagram)", "Has an AROHA account and uses news, manual link checks, audio analysis and "
     "lip-sync analysis with uploaded files.", "Basic"),
    ("Instagram professional user", "Registered user with an eligible Creator or Business account connected through "
     "Meta, who also uses analytics and account-linked checks.", "Basic to Medium"),
    ("Personal-account user", "Registered user whose Instagram account is personal. Cannot use Instagram API features, "
     "is told how to switch to a professional account and keeps access to all other features.", "Basic"),
    ("Researcher / Admin", "Manages research datasets, annotations, model versions and evaluation reports, and "
     "monitors jobs.", "Medium to High"),
]

ENVIRONMENT = [
    "**Client:** any modern web browser (current Chrome, Edge, Firefox or Safari) on desktop, laptop, tablet or mobile.",
    "**Server:** Python 3.11 or later with FastAPI; PostgreSQL; Redis; Celery workers; FFmpeg installed on the worker "
    "machines; PyTorch-based models running on CPU, or on an NVIDIA GPU where available.",
    "**Frontend build:** Node.js (current LTS), Next.js, React, TypeScript, Tailwind CSS.",
    "**Network:** HTTPS access to Meta's Instagram API, news sources and an SMTP service.",
]

ASSUMPTIONS = [
    "AROHA will use **Instagram API with Instagram Login** (Business Login for Instagram), which needs no linked "
    "Facebook Page, with the permissions `instagram_business_basic` and `instagram_business_manage_insights`. This "
    "choice and the details below were gathered from Meta's public documentation and secondary summaries and must be "
    "re-verified against the official documentation before implementation, because Meta changes metrics, "
    "versions and permissions.",
    "During development, accounts owned by or added to the Meta app can be used with Standard Access. Serving other "
    "people's professional accounts publicly needs **Advanced Access**, which involves App Review and business "
    "verification. If Advanced Access is not granted, public Instagram connection cannot be offered and the "
    "application will run those features only for accounts that the team controls, while all other features stay "
    "public.",
    "The API serves professional accounts only. Meta's Basic Display API for personal accounts was discontinued in "
    "December 2024, so personal accounts cannot be connected.",
    "Account-level insights are retained by Instagram for a limited period (about 90 days), may be delayed by up to "
    "about 48 hours, and some metrics are unavailable for small accounts. AROHA therefore stores its own daily "
    "snapshots from the day of connection and cannot back-fill history that Instagram no longer provides.",
    "Metric names and availability can change (for example, `views` replaced older `impressions` and `plays` "
    "metrics in 2025). All Instagram calls are isolated behind one integration module so changes affect one place.",
    "Media files of a Reel are not guaranteed to be downloadable through the API. Where a file is unavailable, the "
    "user can upload it manually.",
    "Pretrained speech, OCR and audio-visual synchronisation models are available under licences that permit this use.",
    "News sources provide feeds or APIs that may be used within their terms of service.",
    "Users have a working internet connection and upload videos that they own or are permitted to analyse.",
]

# --------------------------------------------------------------------------- 3. Functional requirements
# Each section: key, title, description paragraphs, requirements (text, priority)
FR_SECTIONS = [
    dict(key="auth", title="User Registration and Authentication",
         desc="Anyone can register and sign in. Each user has a separate, private account, and no user may see "
              "another user's data.",
         reqs=[
             ("The system shall allow a visitor to register with a name, e-mail address and password, validating the "
              "e-mail format and password strength on the server.", H),
             ("The system shall reject registration for an e-mail address that is already in use.", M),
             ("The system shall store passwords only as salted hashes produced by a modern password-hashing algorithm "
              "(Argon2id or bcrypt).", H),
             ("The system shall authenticate users by e-mail and password and create a secure session (HTTP-only, "
              "Secure, SameSite cookie or signed short-lived token).", H),
             ("The system shall allow users to log out and shall invalidate the session on the server.", H),
             ("The system shall provide password recovery through a single-use, time-limited reset link sent by e-mail, "
              "without revealing whether an address is registered.", H),
             ("The system shall allow users to view and update their profile and to change their password.", M),
             ("The system shall allow users to delete their account after confirmation and shall then remove their "
              "profile, tokens, uploads, reports and consent records.", H),
             ("The system shall verify on every API request that the requested record belongs to the signed-in user.", H),
             ("The system shall rate-limit authentication endpoints and slow repeated failed sign-in attempts.", H),
             ("The system shall let registered users without a connected Instagram account use every feature that does "
              "not require Instagram API data.", H),
         ]),
    dict(key="ig", title="Instagram Account Connection",
         desc="Eligible Creator and Business accounts connect through Meta's official OAuth flow. AROHA never "
              "handles Instagram passwords.",
         reqs=[
             ("The system shall provide a prominent \u201cConnect Instagram\u201d button that redirects the user to Meta's "
              "official authorisation page.", H),
             ("The system shall use only the supported Instagram OAuth flow and shall request only the permissions it "
              "needs (`instagram_business_basic`, `instagram_business_manage_insights`).", H),
             ("The system shall generate an unpredictable, single-use OAuth `state` value bound to the user's session "
              "and shall reject callbacks with a missing, invalid or expired state.", H),
             ("The system shall exchange the authorisation code for a token on the backend only and shall never expose "
              "the app secret or any token to the browser.", H),
             ("The system shall exchange short-lived tokens for long-lived tokens, renew them before expiry where "
              "supported, and mark the connection as expired and ask the user to reconnect if renewal fails.", H),
             ("The system shall encrypt access tokens at rest using authenticated encryption with a key held in the "
              "environment.", H),
             ("The system shall never ask for, receive or store an Instagram password, extract session cookies or "
              "automate Instagram login.", H),
             ("The system shall display the connected username and account type, and the profile picture when the API "
              "returns it.", M),
             ("The system shall allow the user to disconnect the account, shall delete the stored tokens immediately and "
              "shall offer to delete the synchronised data.", H),
             ("When the account is personal or otherwise ineligible, the system shall explain that a Creator or "
              "Business account is required for API features and shall keep all other features available.", H),
             ("The system shall read `META_APP_ID`, `META_APP_SECRET`, `META_REDIRECT_URI`, `DATABASE_URL`, session or "
              "JWT secrets and other credentials from environment variables and shall never place them in frontend "
              "code or the repository.", H),
             ("The system shall handle API errors (permission denied, expired token, rate limit) with clear user "
              "messages and shall not write tokens to logs.", M),
         ]),
    dict(key="fol", title="Follower and Unfollower Analytics",
         desc="The system stores follower snapshots and calculates growth. It distinguishes metrics supplied by the "
              "API from values that AROHA calculates, and it never identifies individual unfollowers.",
         reqs=[
             ("The system shall retrieve the current follower count and store a snapshot at least daily for each "
              "connected account, recording the source and the calculation method.", H),
             ("The system shall display follower history for the selected date range as a line chart.", H),
             ("The system shall calculate net follower growth (end count minus start count), percentage growth, and "
              "daily, weekly and monthly change from the stored snapshots.", H),
             ("The system shall display new-follower or follow/unfollow counts only where the API provides the metric.", M),
             ("The system shall provide an Unfollowers Analysis page showing API-provided unfollow statistics where "
              "available, net change from snapshots, growth versus decline trends, and daily, weekly and monthly "
              "comparisons.", H),
             ("The system shall label every figure as \u201cAPI metric\u201d or \u201cCalculated from snapshots\u201d and shall "
              "never claim to identify the usernames of people who unfollowed.", H),
             ("The system shall compare follower growth in the selected period with the previous period of equal "
              "length.", M),
             ("When fewer than two snapshots exist or the API returns no data, the system shall explain why instead "
              "of showing zeros or estimates.", H),
             ("The system shall offer date filters for the last 7 days, 30 days, 90 days and a custom range, limited to "
              "the data available.", H),
         ]),
    dict(key="eng", title="Engagement, Growth Analysis and Insights",
         desc="Engagement is calculated with explicitly documented formulas. **Engagement rate by reach** = (total "
              "interactions \u00f7 reach) \u00d7 100. **Engagement rate by followers** = (total interactions \u00f7 followers) "
              "\u00d7 100. **Net follower change** = F(end) \u2212 F(start). **Percentage growth** = (F(end) \u2212 F(start)) \u00f7 "
              "F(start) \u00d7 100. The two engagement definitions are never mixed in one chart.",
         reqs=[
             ("The system shall retrieve likes, comments, shares, saves, reach, views and total interactions at account "
              "and media level where the API provides them, and shall store them with timestamps.", H),
             ("The system shall calculate engagement rate by reach and, optionally, by followers using the formulas "
              "above, shall show which formula is used and shall not mix definitions in one chart.", H),
             ("The system shall provide Recharts visualisations: a line chart of follower growth, a bar chart of "
              "engagement comparison, an area chart of account growth, a pie chart of engagement distribution and a "
              "performance table of posts and Reels.", H),
             ("The system shall show best-performing content and top-performing Reels for a selected metric.", M),
             ("The system shall show weekly and monthly performance comparison and engagement growth.", M),
             ("The system shall generate insights from calculations (for example, an increase or decrease compared "
              "with the previous period) and may add an AI-written explanation of those computed values.", M),
             ("When data is insufficient, the system shall say so instead of generating insights.", H),
             ("The system shall mark metrics that the API does not support, or restricts for the account, as "
              "\u201cNot available\u201d and shall not invent values.", H),
             ("The system shall provide a clearly labelled demo mode that uses separate demonstration data and never "
              "mixes it with real data.", H),
             ("The analytics page shall show a welcome message, connection status, a date selector and cards for "
              "followers, new followers, unfollows (where available), engagement and reach.", M),
         ]),
    dict(key="link", title="Broken Promotional Link Analyzer",
         desc="The analyzer finds links in several sources and validates them safely. It reports uncertainty "
              "honestly: a 403 response or a temporary timeout is not proof that a link is broken.",
         reqs=[
             ("The system shall accept URLs entered manually (single or in a list) for validation without an Instagram "
              "connection.", H),
             ("The system shall extract URLs from the connected account's bio link and from captions when available.", H),
             ("The system shall accept a video upload and extract frames at a configurable interval using OpenCV.", H),
             ("The system shall run OCR on frames and extract URLs and website addresses shown as text.", H),
             ("The system shall detect and decode QR codes in video frames.", H),
             ("The system shall transcribe speech and extract spoken URLs, treating them as lower-confidence "
              "candidates.", M),
             ("When a promotional phrase such as \u201clink in bio\u201d is detected, the system shall associate it with the "
              "account's bio link if available and shall not invent a product URL.", H),
             ("The system shall classify promotional content with rules and pretrained models into product promotion, "
              "affiliate marketing, website promotion, discount advertisement, shopping recommendation or "
              "non-promotional.", M),
             ("The system shall normalise and de-duplicate URLs before validation.", M),
             ("The system shall check each URL for HTTP status (200, 301/302, 403, 404, 500), DNS failure, TLS/"
              "certificate problems, timeouts, excessive redirect chains and suspicious destinations.", H),
             ("The system shall report 403 responses and temporary timeouts as \u201cUnverified\u201d unless repeated checks "
              "show failure.", H),
             ("The system shall prevent SSRF: allow only http and https, resolve the host and block private, loopback, "
              "link-local, multicast and cloud-metadata addresses, revalidate every redirect hop, and apply timeouts, "
              "a redirect limit and a maximum response size.", H),
             ("The system shall assign one of the statuses Working, Broken, Redirected, Suspicious or Unverified to "
              "each URL.", H),
             ("The system shall display for each result the associated Reel or post, detection source, detected URL, "
              "status, HTTP code, problem description, detection date and suggested correction.", H),
             ("The system shall store results, show a detailed report and allow export (CSV and PDF).", M),
             ("The system shall run video processing as a background job with progress reporting.", H),
         ]),
    dict(key="audio", title="Reel Audio Loss Detector",
         desc="The detector compares the audio of a current video with a stored reference. It distinguishes a silent or "
              "missing track inside a file from a licensed music track becoming unavailable on Instagram, which "
              "the official API may not report.",
         reqs=[
             ("The system shall accept an original reference video or audio file, extract its audio with FFmpeg, "
              "compute a fingerprint and store the fingerprint and metadata.", H),
             ("The system shall retain the reference file only if the user has given explicit consent; otherwise it "
              "shall delete the file after analysis.", H),
             ("The system shall accept a current version (upload, or accessible media through the API) and compute "
              "its fingerprint.", H),
             ("The system shall detect a missing audio stream, completely silent audio, unexpected silent segments "
              "and audio discontinuities.", H),
             ("The system shall compare reference and current fingerprints, tolerating small time shifts, and "
              "calculate a similarity score.", H),
             ("The system shall classify each result as Audio available, No audio track, Silent audio, Possible audio "
              "replacement, Significant audio change or Unable to verify.", H),
             ("The system shall display a report with the Reel identifier, original reference, current status, "
              "fingerprint comparison, detection time, similarity score and recommended action.", H),
             ("The system shall display waveforms of the reference and current audio and highlight differing "
              "time ranges.", M),
             ("The system shall keep a history of analyses and let the user compare an earlier reference with "
              "current content.", M),
             ("When no earlier reference or media is accessible, the system shall display \u201cUnable to verify previous "
              "audio status.\u201d", H),
             ("The system shall not claim that the API reports every Instagram audio-removal event, and shall "
              "separate file-level silence from platform-level music unavailability in its wording.", H),
         ]),
    dict(key="lip", title="AI-Based Lip-Sync Mismatch Analyzer",
         desc="This is the principal AI/ML research module. It uses a pretrained audio-visual synchronisation model; "
              "facial landmarks alone are not treated as proof of synchronisation. Sign convention: a positive offset "
              "means the audio is ahead of the video.",
         reqs=[
             ("The system shall accept video uploads and validate extension, MIME type, container and codec "
              "(using FFprobe), size and duration limits.", H),
             ("The system shall extract mono audio at a fixed sampling rate and video frames at a fixed frame rate.", H),
             ("The system shall detect faces and track the mouth region using facial landmarks.", H),
             ("The system shall detect speech activity and shall return \u201cInsufficient data\u201d when there is not "
              "enough speech with a visible face.", H),
             ("The system shall evaluate audio-video synchronisation with a pretrained audio-visual model (SyncNet or "
              "an evaluated alternative).", H),
             ("The system shall estimate the audio-video offset in milliseconds and a confidence score.", H),
             ("The system shall classify each video as Properly synchronized, Minor synchronization mismatch, "
              "Significant synchronization mismatch, Audio ahead of video, Video ahead of audio or Insufficient data, "
              "using documented thresholds.", H),
             ("The system shall identify time windows with a potential mismatch and let the user jump to that "
              "timestamp in the video preview.", H),
             ("The system shall display the video preview, status, estimated offset, confidence, problem timestamps, "
              "audio waveform, analysis timeline and suggested corrections.", H),
             ("The system shall not treat pauses, music videos, background music, dubbing or creative editing as "
              "automatic errors and shall explain uncertain results.", H),
             ("The system shall run the analysis as a background job with progress and status polling.", H),
             ("The system shall support evaluation runs that compute the metrics listed in Section 3.10.", M),
         ]),
    dict(key="news", title="Social Media Trends and Latest News",
         desc="The news module is open to every registered user. It uses licensed or public feeds and does not scrape "
              "unauthorised sources.",
         reqs=[
             ("The system shall collect articles on a schedule from official announcements, RSS feeds and licensed "
              "news APIs, respecting each source's terms of use.", H),
             ("The system shall store the title, summary, source name, publication date, event date (when "
              "available), thumbnail, category and original article URL.", H),
             ("The system shall de-duplicate articles by canonical URL, cache results and record source metadata and "
              "fetch time.", H),
             ("The system shall assign articles to the ten categories (Instagram Updates, Instagram Algorithm "
              "Changes, Reels Trends, Trending Content Formats, Influencer Marketing, Social Media Marketing, Creator "
              "Economy, AI Tools for Content Creators, Digital Marketing, Social Media Industry News) using a "
              "documented keyword taxonomy.", M),
             ("The system shall provide the filters Latest, Instagram, Reels, Marketing, AI and Technology and "
              "Influencer Trends, with search, sorting and pagination.", H),
             ("The system shall display trending topics derived from recent articles and shall label official "
              "announcements separately from emerging or unverified trends.", M),
             ("The system shall display each article as a card with headline, short summary, source, date, "
              "thumbnail and category, linking to the original article.", H),
             ("The system shall continue to show cached articles and display a notice when a source is "
              "unavailable.", M),
             ("The system shall make the module available without a connected Instagram account.", H),
         ]),
    dict(key="ui", title="User Interface, Navigation and Branding",
         desc="The interface is an original, Pinterest-inspired design with its own logo, palette and components. "
              "It must not copy Pinterest's interface and must not use a red-dominant scheme.",
         reqs=[
             ("The system shall provide a public landing page with AROHA branding, the headline \u201cUnderstand Your "
              "Social Media. Discover What Matters.\u201d, Get Started and Connect Instagram buttons, a feature showcase, "
              "a dashboard preview, AI feature explanations, a security and privacy section and a footer.", H),
             ("The system shall use one shared application layout with a single collapsible left sidebar and shall "
              "not duplicate the sidebar on individual pages.", H),
             ("The expanded sidebar shall show the AROHA logo and wordmark and links to Home, Analytics Dashboard, "
              "Unfollowers, Growth Analysis, Broken Link Analyzer, Audio Loss Detector, Lip-Sync Analyzer, Trends and "
              "News, Connect Instagram, Settings and User Profile.", H),
             ("The collapsed sidebar shall show the AROHA A symbol, navigation icons with hover tooltips and an "
              "expand button, the main content shall adjust automatically, and the transition shall be smooth.", H),
             ("The system shall remember the sidebar state across navigation and sessions and highlight the active "
              "item.", M),
             ("The system shall provide a slide-out drawer on mobile and keyboard navigation for the sidebar.", H),
             ("The system shall provide a top bar with search, notifications, Instagram connection status, a "
              "profile avatar with account menu and an optional theme toggle.", M),
             ("The system shall use an original geometric A lettermark in SVG, with light, dark, favicon, "
              "application-icon and loading variants.", M),
             ("The system shall use consistent design tokens: Midnight Navy #17212B, Soft Ivory #F7F8F5, Muted Teal "
              "#2A9D8F, Soft Lavender #A78BFA and Warm Amber #E9B44C, with sufficient text contrast.", M),
             ("The system shall use responsive masonry layouts for news, trends, visual insights, Reel previews and "
              "promotional results, and structured layouts for analytics dashboards.", M),
             ("The system shall be usable on desktop, laptop, tablet and mobile, including charts, tables and upload "
              "screens.", H),
             ("The system shall provide loading skeletons, toast notifications, modal dialogs, dropdown menus, "
              "progress indicators and clear empty, success and error states.", M),
             ("Every navigation link and button shall perform a real action; no placeholder controls shall be "
              "shipped.", H),
         ]),
    dict(key="priv", title="Privacy, Consent, Datasets and Model Evaluation",
         desc="Uploaded media is private. Retention and model training each need separate, explicit consent. "
              "Evaluation results are reported only from real, measured experiments.",
         reqs=[
             ("The system shall require explicit opt-in before retaining an uploaded file for historical comparison; "
              "the default shall be off.", H),
             ("The system shall require a separate opt-in before a user's uploads or data are used for model "
              "training; the default shall be off, and production user data shall not be used for training by "
              "default.", H),
             ("The system shall let users view and withdraw each consent; withdrawal shall remove retained media and "
              "exclude the data from future training, and shall be recorded with timestamps.", H),
             ("The system shall provide a dataset management module for researchers and administrators supporting "
              "uploads, file validation, annotation, labels, dataset versions, training/validation/test splits and "
              "licence metadata.", M),
             ("The system shall split datasets so that speakers and source videos do not appear in more than one of "
              "the training, validation and test sets where practical.", M),
             ("The system shall track model versions and store evaluation reports with dataset composition, method, "
              "environment and limitations.", M),
             ("The system shall compute accuracy, precision, recall, F1-score, confusion matrix, ROC-AUC, mean "
              "absolute error of the offset estimate and processing time on a held-out set, compare the result "
              "with a baseline, and report only measured values.", H),
             ("The system shall accept only datasets that are publicly licensed, appropriately licensed or "
              "collected with consent.", H),
         ]),
    dict(key="job", title="Background Jobs, Reports, Uploads and Audit",
         desc="Expensive work runs outside normal requests. Uploads are validated, temporary files are removed and "
              "security-relevant events are logged.",
         reqs=[
             ("The system shall run video and audio analysis through a job queue and the API shall return a job "
              "identifier immediately.", H),
             ("The system shall record for each job its type, status (queued, running, succeeded, failed, "
              "cancelled), progress and timestamps.", H),
             ("The system shall provide a status endpoint that the interface polls, shall apply timeouts and "
              "retries, and shall show a readable message when a job fails.", H),
             ("The system shall generate reports for link, audio and lip-sync analyses that can be viewed in the "
              "application and exported.", M),
             ("The system shall delete temporary files after processing or at expiry.", H),
             ("The system shall write audit logs for sign-in, token events, data deletion and consent changes, "
              "without recording secrets.", M),
             ("The system shall validate uploads by size, MIME type, extension and content signature, and shall "
              "reject files that fail.", H),
             ("The system shall return consistent error responses with appropriate HTTP status codes.", M),
         ]),
]

# --------------------------------------------------------------------------- 4. External interfaces
UI_REQS = [
    "A responsive web interface built with Next.js, React and Tailwind CSS, usable from 360 px wide screens upward.",
    "Public pages: landing, login, registration and password recovery. Signed-in pages: dashboard, analytics, "
    "unfollowers, growth, link analyzer, audio detector, lip-sync analyzer, trends and news, settings and profile.",
    "Consistent design tokens, an original A lettermark, a single collapsible sidebar and a top bar.",
    "Accessible controls: keyboard navigation, visible focus, text alternatives and adequate colour contrast.",
]

HARDWARE = [
    ("Client device", "Any device with a modern browser and internet access", "Desktop or laptop for large dashboards"),
    ("Server CPU", "4 cores", "8 cores or more"),
    ("Server memory", "16 GB", "32 GB when several analyses run in parallel"),
    ("GPU (optional)", "Not required; models run on CPU", "NVIDIA GPU with CUDA to speed up inference"),
    ("Storage", "50 GB SSD", "200 GB SSD for media and datasets"),
    ("Network", "Stable broadband", "HTTPS-capable public endpoint for OAuth redirect"),
]

SOFTWARE = [
    ("Python 3.11+", "Backend and AI language"),
    ("FastAPI, Pydantic", "REST API and request validation"),
    ("SQLAlchemy, Alembic", "Object-relational mapping and database migrations"),
    ("PostgreSQL", "Primary relational database"),
    ("Redis, Celery", "Message broker and background workers"),
    ("Next.js, React, TypeScript", "Frontend framework and language"),
    ("Tailwind CSS, Recharts, Lucide React", "Styling, charts and icons"),
    ("OpenCV", "Frame extraction and QR code detection"),
    ("EasyOCR or PaddleOCR", "Text recognition in video frames"),
    ("Whisper", "Speech recognition"),
    ("FFmpeg / FFprobe", "Audio and video extraction and inspection"),
    ("librosa, NumPy, SciPy", "Audio feature extraction and fingerprinting"),
    ("MediaPipe", "Face detection and facial landmarks"),
    ("PyTorch", "Pretrained audio-visual synchronisation model inference"),
    ("HTTPX", "Safe HTTP validation of links and feed requests"),
    ("Meta Instagram API", "Instagram OAuth, account insights and media metadata"),
    ("News API / RSS feeds", "Social media news and trends"),
    ("SMTP service", "Password-recovery e-mail"),
]

COMMS = [
    "HTTPS (TLS) for all browser-to-server and server-to-external traffic in deployment.",
    "REST over JSON; multipart/form-data for uploads; consistent error format.",
    "OAuth 2.0 authorisation-code redirect and callback with `state` validation.",
    "Redis protocol between the API and Celery workers (internal network only).",
    "SMTP for password-recovery e-mail.",
]

API_SUMMARY = [
    ("Authentication", "POST /auth/register, POST /auth/login, POST /auth/logout, POST /auth/forgot-password, "
     "GET /auth/me"),
    ("Instagram", "GET /instagram/connect, GET /instagram/callback, GET /instagram/account, POST "
     "/instagram/disconnect, GET /instagram/analytics, GET /instagram/media, GET /instagram/growth"),
    ("Link Analyzer", "POST /links/analyze, POST /links/extract-from-video, GET /links/reports, GET "
     "/links/reports/{report_id}"),
    ("Audio Detector", "POST /audio/upload-reference, POST /audio/analyze, GET /audio/history, GET "
     "/audio/report/{report_id}"),
    ("Lip-Sync", "POST /lipsync/upload, POST /lipsync/analyze, GET /lipsync/status/{job_id}, GET "
     "/lipsync/report/{report_id}"),
    ("News", "GET /news, GET /news/categories, GET /news/trending, GET /news/{article_id}"),
    ("User settings", "GET /users/profile, PUT /users/profile, GET /users/settings, DELETE /users/account"),
]

# --------------------------------------------------------------------------- 5. NFR
NFRS = [
    ("Performance", "Non-analysis API requests should complete within 2 seconds at the 95th percentile under normal load."),
    ("Performance", "Dashboard pages should show loading skeletons immediately and become interactive within 3 "
                    "seconds on broadband for cached data."),
    ("Performance", "Video and audio analyses shall run asynchronously. Processing time per minute of video shall be "
                    "measured on the reference machine and reported; no figure is assumed in advance."),
    ("Scalability", "The API shall be stateless, and analysis capacity shall scale by adding workers."),
    ("Security", "All traffic in deployment shall use HTTPS, with secure HTTP headers."),
    ("Security", "Passwords shall be hashed, tokens encrypted at rest, and secrets kept in environment variables, "
                 "never in source code or the frontend."),
    ("Security", "The system shall validate all input, use parameterised database access, protect cookie sessions "
                 "against CSRF, and restrict CORS to the application's own origin."),
    ("Security", "The system shall apply rate limiting, SSRF protection and strict upload validation."),
    ("Privacy", "The system shall store only data needed for its functions, require consent for retention and "
                "training, and delete user data on request."),
    ("Reliability", "A failed job shall not affect API availability; jobs shall have timeouts and retries; database "
                    "writes shall be transactional."),
    ("Availability", "The system shall degrade gracefully when Meta, news sources or the e-mail service are "
                     "unavailable, and say what is unavailable."),
    ("Data integrity", "The system shall never display fabricated data as real. Every result shall state its source "
                       "(API, calculation or model), and demonstration data shall be separate and labelled."),
    ("Explainability", "Each AI result shall include a status, a score or confidence, and a plain-language "
                       "explanation, including when the result is uncertain."),
    ("Usability", "Navigation shall be consistent, error messages clear, and empty, loading and error states "
                  "provided on every page."),
    ("Accessibility", "The interface shall support keyboard navigation, visible focus and ARIA labels, and aim for "
                      "WCAG 2.1 AA contrast."),
    ("Compatibility", "The interface shall work on current versions of Chrome, Edge, Firefox and Safari at screen "
                      "widths from 360 px."),
    ("Maintainability", "Code shall be modular, typed (TypeScript and Python type hints), documented, and covered by "
                        "unit tests for all calculation and classification functions."),
    ("Portability", "The system shall run on Windows and Linux with configuration through environment variables."),
    ("Extensibility", "Platform integrations shall sit behind a common interface so other platforms can be added "
                      "without changing existing modules."),
    ("Observability", "The system shall produce structured logs and audit events that contain no passwords, tokens or "
                      "private media."),
    ("Compliance", "The system shall follow Meta's Platform Terms and Developer Policies, publish a privacy policy "
                   "and provide data-deletion instructions."),
]

# --------------------------------------------------------------------------- 6. Diagrams
DIAGRAM_TEXT = {
    "dfd0": "The context diagram shows AROHA as a single process. Users send credentials, uploads, URLs and filters and "
            "receive dashboards, reports and news. Meta's Instagram API exchanges authorisation and account data, news "
            "sources supply articles, an e-mail service delivers password-reset messages, and researchers supply "
            "datasets and evaluation requests.",
    "dfd1": "The Level 1 diagram splits AROHA into seven processes: authentication and user management, Instagram "
            "connection, metric synchronisation and analysis, link analysis, audio loss detection, lip-sync analysis "
            "and news collection. Five data stores hold users and consent, accounts and analytics history, media and "
            "reports, jobs and lip-sync results, and news articles.",
    "arch": "AROHA uses four layers. The presentation layer is the Next.js client. The application layer is the FastAPI "
            "service with one router per feature. The processing layer runs the Celery workers that contain the AI "
            "pipelines. The data and external layer contains PostgreSQL, media storage, Meta's API and news sources.",
    "usecase": "The use case diagram shows four actors. Registered users perform the features that need no Instagram "
               "data. Instagram professional users also connect an account and view analytics. Meta's platform is a "
               "secondary actor for authorisation and data. Researchers or administrators manage datasets and "
               "evaluate the lip-sync model.",
}

# --------------------------------------------------------------------------- 7. Data
DATA_REQS = [
    "**Account data:** name, e-mail and password hash for each user; authentication and consent records.",
    "**Instagram data:** connected account identifiers, encrypted tokens and expiry, daily follower and engagement "
    "snapshots, and media metadata (identifier, type, caption, timestamps). Only data needed for the features is "
    "stored.",
    "**Analysis data:** extracted links with validation results, audio fingerprints and audio analysis results, "
    "lip-sync results and reports, and background job records.",
    "**Uploaded media:** stored temporarily for processing and deleted afterwards unless the user has consented to "
    "retention.",
    "**News data:** article metadata and source information fetched from feeds, shared by all users.",
    "**Research data:** publicly licensed, appropriately licensed or consented datasets with annotations, versions, "
    "splits and evaluation reports.",
    "**Retention:** data is deleted when the user deletes the account or disconnects and chooses to delete "
    "synchronised data.",
]

TABLES = [
    ("users", "id (PK), name, email (unique), password_hash, created_at, updated_at"),
    ("connected_accounts", "id (PK), user_id (FK), platform, platform_user_id, username, encrypted_access_token, "
     "token_expiry, connection_status, created_at; unique (platform, platform_user_id)"),
    ("analytics_history", "id (PK), connected_account_id (FK), metric_name, metric_value, reporting_period, "
     "captured_at, source, calculation_method"),
    ("media_items", "id (PK), user_id (FK), platform_media_id, media_type, media_reference, caption, created_at"),
    ("link_analysis", "id (PK), user_id (FK), media_id (FK, nullable), detected_url, response_status, "
     "validation_result, issue_description, checked_at"),
    ("audio_references", "id (PK), user_id (FK), media_id (FK, nullable), audio_fingerprint, reference_file "
     "(nullable), created_at"),
    ("audio_analysis", "id (PK), user_id (FK), media_id (FK, nullable), detected_status, similarity_score, "
     "analysis_date"),
    ("lipsync_analysis", "id (PK), user_id (FK), video_reference, synchronization_status, estimated_offset_ms, "
     "confidence_score, analysis_report, created_at"),
    ("news_articles", "id (PK), title, description, source, article_url (unique), category, published_at, "
     "fetched_at"),
    ("background_jobs", "id (PK), user_id (FK), job_type, job_status, progress, created_at, completed_at"),
    ("consent_records", "id (PK), user_id (FK), consent_type, consent_status, recorded_at, withdrawn_at"),
]

DB_NOTES = [
    "Foreign keys use ON DELETE CASCADE from `users` so that deleting an account removes its dependent rows.",
    "Indexes: unique index on `users.email`; unique index on `news_articles.article_url`; composite index on "
    "`analytics_history (connected_account_id, metric_name, captured_at)`; index on `(user_id, created_at)` for "
    "report tables and `background_jobs`.",
    "Constraints: `consent_type` and `job_status` use enumerated values; `similarity_score` and `confidence_score` are "
    "limited to 0\u20131; timestamps are stored in UTC.",
    "The schema is created and changed only through versioned Alembic migrations.",
]

# --------------------------------------------------------------------------- 8. Constraints
CONSTRAINTS = [
    "The first version supports Instagram only.",
    "Instagram features are bound by Meta's permissions, review process, rate limits and terms. Public connection of "
    "other people's accounts needs Advanced Access.",
    "Only publicly licensed, appropriately licensed or consented datasets may be used, and pretrained models must "
    "have licences that permit the intended use.",
    "The project must be completed within the academic schedule by one student, with limited computing resources.",
    "Heavy analysis must run in background workers, not inside normal API requests.",
    "Secrets must be supplied through environment variables.",
]

LIMITATIONS = [
    "Personal Instagram accounts cannot be connected to the API; they can use the upload-based features.",
    "Instagram does not provide the identities of unfollowers, and account insights are retained for a limited "
    "period. AROHA can show only aggregate API metrics and net changes from its own snapshots, and history before "
    "connection cannot be recovered.",
    "Some metrics are unavailable for small accounts or may be changed or removed by Meta.",
    "Reel media files may not be downloadable through the API. Where unavailable, manual upload is required.",
    "Instagram licensed-music removal on the platform may not be visible through the API. AROHA detects silence, "
    "absence or change only in files it can analyse.",
    "Lip-sync analysis needs a visible face and clear speech. Music videos, dubbing, voice-over and heavy editing "
    "may give uncertain results.",
    "OCR and speech recognition can misread URLs, so extracted links are validated and shown with their source.",
    "Link validation cannot always distinguish a blocked crawler from a broken page, which is why some results are "
    "Unverified.",
    "Model accuracy will be measured on a small held-out set and may not generalise to all videos.",
]

# --------------------------------------------------------------------------- 9. Testing
TEST_APPROACH = [
    "**Unit testing:** authentication functions, engagement and growth calculations, URL extraction, HTTP "
    "validation, audio fingerprint comparison, lip-sync classification and news categorisation.",
    "**Integration testing:** frontend-backend communication, Instagram OAuth (against Meta's test setup), database "
    "operations, background job processing, file upload and AI model inference.",
    "**System testing:** the complete workflow from registration to report generation for each feature.",
    "**Security testing:** unauthorised access, cross-user data leakage, malicious and internal URLs, file upload "
    "validation, invalid tokens and session handling.",
    "**AI/ML evaluation:** the lip-sync module on a held-out labelled dataset, recording dataset composition, "
    "method, test environment, model version, metrics and limitations.",
]

# (section key, test case, expected result)
TESTS = [
    ("auth", "Register with a valid name, e-mail and strong password.",
     "Account is created, the password is stored only as a hash, and the user can sign in."),
    ("auth", "Register with an invalid e-mail or a weak password.", "A validation error is shown and no account is created."),
    ("auth", "Sign in repeatedly with a wrong password.", "A generic error is shown and attempts are throttled after the limit."),
    ("auth", "Use a password-reset link twice, and after expiry.", "The first use succeeds; the second and expired uses are rejected."),
    ("auth", "User A requests a report owned by user B.", "The request is refused (403 or 404) and no data is returned."),
    ("auth", "Delete the account.", "Profile, tokens, uploads, reports and consents are removed and sign-in fails."),
    ("ig", "Click Connect Instagram.", "The browser is redirected to Meta's authorisation page with the required scopes and a state value."),
    ("ig", "Send a callback with a missing or altered state.", "The callback is rejected and no token is stored."),
    ("ig", "Authorise an eligible professional account.", "The token is stored encrypted; username and account type are shown; the token never appears in API responses or browser storage."),
    ("ig", "Disconnect Instagram.", "Tokens are deleted, status becomes Disconnected, and non-Instagram features still work."),
    ("ig", "Try to connect a personal account.", "An explanation about switching to Creator or Business is shown and other features remain available."),
    ("ig", "Use an expired token.", "Renewal is attempted; on failure the status is Expired and the user is asked to reconnect."),
    ("fol", "Run the growth calculation on known follower snapshots.", "Daily, weekly, monthly, net and percentage growth match hand-calculated values."),
    ("fol", "Open Unfollowers with snapshot data only.", "Net change is shown labelled \u201cCalculated\u201d, no usernames appear, and unavailable API metrics are marked."),
    ("fol", "Open analytics with fewer than two snapshots.", "An explanatory message appears instead of zeros or estimates."),
    ("fol", "Switch the date filter between 7, 30, 90 days and a custom range.", "Cards and charts update to the chosen range."),
    ("eng", "Call the engagement-rate function with known values, including reach = 0.", "It returns interactions \u00f7 reach \u00d7 100 and interactions \u00f7 followers \u00d7 100, and handles zero without error."),
    ("eng", "Open the dashboard with data.", "Line, bar, area and pie charts and the performance table render, and the formula used is shown."),
    ("eng", "Request a metric the API does not provide.", "\u201cNot available\u201d is shown and no value is invented."),
    ("eng", "Enable demo mode.", "A demo banner is visible and demo data is separate from real data."),
    ("link", "Extract URLs from sample captions with punctuation, duplicates and shortened links.", "Correct, normalised, unique URLs are returned."),
    ("link", "Process a video frame showing a printed URL.", "The URL is detected through OCR."),
    ("link", "Process a video frame containing a QR code.", "The QR code is decoded and its URL listed."),
    ("link", "Process a Reel that says \u201clink in bio\u201d.", "It is mapped to the account's bio link and no URL is invented."),
    ("link", "Validate a test server returning 200, 301, 403, 404, 500 and a timeout.", "Results are Working, Redirected, Unverified, Broken, Broken (server error) and Unverified respectively."),
    ("link", "Submit http://127.0.0.1, a 10.x address, 169.254.169.254 and localhost.", "All are blocked, no request is sent, and each is reported as unsafe."),
    ("link", "Submit a public URL that redirects to a private address.", "The redirect hop is revalidated and blocked."),
    ("link", "Submit a URL with a long or looping redirect chain.", "Following stops at the limit and the link is flagged for excessive redirects."),
    ("link", "Export a link report.", "The file contains all result fields."),
    ("audio", "Analyse a video that has no audio stream.", "Status is No audio track."),
    ("audio", "Analyse a completely silent file.", "Status is Silent audio."),
    ("audio", "Compare a reference with a re-encoded copy of itself.", "Status is Audio available with a high similarity score."),
    ("audio", "Compare a reference with a file whose audio was replaced.", "Status is Possible audio replacement or Significant audio change with a low score."),
    ("audio", "Analyse without any stored reference.", "\u201cUnable to verify previous audio status.\u201d is shown."),
    ("audio", "Run an analysis with retention consent switched off.", "The reference file is deleted after analysis and only permitted metadata remains."),
    ("lip", "Upload a spoofed, non-video or over-limit file.", "The upload is rejected with a clear error."),
    ("lip", "Analyse a correctly synchronised speaking clip.", "Result is Properly synchronized with an offset inside the tolerance."),
    ("lip", "Analyse a clip whose audio was delayed by a known amount.", "Result is Video ahead of audio, with an offset close to the known value."),
    ("lip", "Analyse a clip whose audio was advanced by a known amount.", "Result is Audio ahead of video, with an offset close to the known value."),
    ("lip", "Analyse a music-only or faceless clip.", "Result is Insufficient data with an explanation."),
    ("lip", "Click a problem timestamp in the results.", "The video preview jumps to that time."),
    ("lip", "Run the evaluation on the held-out set.", "Metrics are computed and stored with dataset and model versions."),
    ("news", "Run the feed collector twice.", "No duplicate articles are created."),
    ("news", "Filter, search, sort and paginate articles.", "Results and counts are correct."),
    ("news", "Open a news card.", "The original article opens, and source and date are shown."),
    ("news", "Make one source unreachable.", "Cached articles still appear and a notice is shown."),
    ("ui", "Toggle the sidebar, navigate and reload.", "Layout adjusts, the state persists, the active item is highlighted and tooltips appear when collapsed."),
    ("ui", "Open the application at 360 px width.", "The mobile drawer works and charts and tables remain usable."),
    ("ui", "Navigate using the keyboard only.", "All sidebar items are reachable with visible focus."),
    ("ui", "Open the landing page.", "All required sections are present and the buttons work."),
    ("priv", "Upload a file with default settings.", "Retention and training opt-ins are unchecked."),
    ("priv", "Withdraw retention consent.", "Retained media is deleted and the consent record shows a withdrawal time."),
    ("job", "Start a lip-sync analysis.", "A job identifier is returned at once and status moves from queued to running to succeeded with progress."),
    ("job", "Force a worker failure.", "The job is marked failed with a readable message, the API stays responsive and temporary files are cleaned."),
    ("job", "Send an expired token, an oversize file, a wrong MIME type and excess requests.", "The API returns 401, 413, 415 and 429 respectively."),
]

ACCEPTANCE = [
    "**Public application:** any user can reach the public site, register, sign in and manage the account, and users "
    "without Instagram can use all independent features.",
    "**Instagram:** eligible accounts connect through official authorisation, tokens are managed securely, available "
    "analytics are retrieved and displayed, and unsupported metrics are identified.",
    "**Analytics:** history is stored, growth calculations are correct, and charts use real data or clearly labelled "
    "demonstration data.",
    "**Link detection:** URLs are extracted from supported sources, links are checked safely, and reports show "
    "reliable statuses and errors.",
    "**Audio detection:** a reference can be stored, current audio compared, and changes and uncertainty reported "
    "correctly.",
    "**Lip-sync detection:** videos can be uploaded and processed, results generated, and metrics calculated on a "
    "held-out dataset.",
    "**Trends and news:** news is collected from supported sources, can be filtered, and each article links to its "
    "original source.",
    "**UI/UX:** AROHA has an original A logo, the sidebar expands and collapses correctly, there is no Pinterest-red "
    "branding, pages are responsive and every button performs a real action.",
    "**Deliverables:** working source code, database schema, documentation, diagrams, test cases, measured AI "
    "results, README, user manual and the final report.",
]

# --------------------------------------------------------------------------- 10. RTM
# (objective, [fr section keys], module, [test section keys])
RTM = [
    ("Provide secure registration, authentication and private accounts", ["auth"], "Authentication service", ["auth"]),
    ("Connect eligible Instagram accounts through official OAuth with protected tokens", ["ig"], "Instagram OAuth service", ["ig"]),
    ("Show follower growth and unfollow-related analytics honestly", ["fol"], "Follower history service", ["fol"]),
    ("Calculate engagement, growth and insights with documented formulas", ["eng"], "Analytics service", ["eng"]),
    ("Detect broken, expired or suspicious promotional links safely", ["link"], "Link extraction and validation service", ["link"]),
    ("Detect missing, silent or changed Reel audio", ["audio"], "Audio fingerprinting service", ["audio"]),
    ("Detect audio-video synchronisation mismatch with measured accuracy", ["lip"], "Lip-sync analysis service", ["lip"]),
    ("Provide social media news and trends", ["news"], "News collection service", ["news"]),
    ("Deliver an original, responsive, accessible interface", ["ui"], "Frontend application", ["ui"]),
    ("Protect privacy and manage datasets and evaluation", ["priv"], "Consent and dataset services", ["priv"]),
    ("Run background jobs, reports, uploads and auditing", ["job"], "Job and report services", ["job"]),
]

REFERENCES = [
    "[1] ISO/IEC/IEEE 29148:2018. Systems and software engineering \u2014 Life cycle processes \u2014 Requirements "
    "engineering.",
    "[2] IEEE Std 830-1998. IEEE Recommended Practice for Software Requirements Specifications.",
    "[3] Meta Platforms, Inc. (2026). Instagram Platform documentation: Instagram API with Instagram Login; Business "
    "Login for Instagram; Insights. Meta for Developers. https://developers.facebook.com/docs/instagram-platform "
    "(accessed 2 November 2026).",
    "[4] Hardt, D. (Ed.) (2012). The OAuth 2.0 Authorization Framework. IETF RFC 6749.",
    "[5] Jones, M., Bradley, J., & Sakimura, N. (2015). JSON Web Token (JWT). IETF RFC 7519.",
    "[6] OWASP Foundation. Server-Side Request Forgery Prevention Cheat Sheet. https://cheatsheetseries.owasp.org",
    "[7] OWASP Foundation. Application Security Verification Standard (ASVS). https://owasp.org/www-project-"
    "application-security-verification-standard/",
    "[8] Chung, J. S., & Zisserman, A. (2016). Out of time: automated lip sync in the wild. Workshop on Multi-view "
    "Lip-reading, Asian Conference on Computer Vision (ACCV).",
    "[9] Wang, A. (2003). An industrial-strength audio search algorithm. Proceedings of the 4th International "
    "Conference on Music Information Retrieval (ISMIR).",
    "[10] Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). Robust speech "
    "recognition via large-scale weak supervision. Proceedings of the 40th International Conference on Machine "
    "Learning (ICML), PMLR 202.",
    "[11] Prajwal, K. R., Mukhopadhyay, R., Namboodiri, V. P., & Jawahar, C. V. (2020). A lip sync expert is all you "
    "need for speech to lip generation in the wild. Proceedings of the 28th ACM International Conference on "
    "Multimedia.",
    "[12] International Telecommunication Union Radiocommunication Sector (1998). Recommendation ITU-R BT.1359-1: "
    "Relative timing of sound and vision for broadcasting.",
    "[13] Lugaresi, C., Tang, J., Nash, H., et al. (2019). MediaPipe: a framework for building perception pipelines. "
    "arXiv:1906.08172.",
    "[14] McFee, B., Raffel, C., Liang, D., Ellis, D. P. W., McVicar, M., Battenberg, E., & Nieto, O. (2015). librosa: "
    "audio and music signal analysis in Python. Proceedings of the 14th Python in Science Conference.",
    "[15] Bradski, G. (2000). The OpenCV Library. Dr. Dobb's Journal of Software Tools.",
    "[16] Baek, Y., Lee, B., Han, D., Yun, S., & Lee, H. (2019). Character region awareness for text detection. "
    "Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR).",
]
