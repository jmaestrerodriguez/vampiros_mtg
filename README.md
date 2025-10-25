# 🚀 Project Name

![Status Badge](https://img.shields.io/badge/Status-In%20Development-yellow)
![License Badge](https://img.shields.io/badge/License-MIT-blue.svg)
---

## 📝 Project Description

A brief one-to-two-sentence description. What problem does this project solve, and what is its main goal?

This project aims to [Describe the main function, e.g.: automate MTG data analysis] and generate [Mention the key output, e.g.: deck performance reports].

---

## 🛠️ Installation and Requirements

These steps will guide you through setting up a functional copy of the project on your local machine.

### Prerequisites

Ensure you have the following installed:

* [Software Name 1, e.g.: Python 3.10+]
* [Software Name 2, e.g.: Git]

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-user/your-repo-name.git](https://github.com/your-user/your-repo-name.git)
    cd your-repo-name
    ```
2.  **Create and activate the virtual environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On Linux/macOS:
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🕹️ Usage
### Local Workflow (Windows)
1. cd to project root.
2. Activate virtual environment.

    ```bash
    Set-ExecutionPolicy Unrestricted -Scope Process
    .venv/Scripts/Activate.ps1
    ```
3. Git setup.
    1. checkout working branch (feat/bugfix). If it doesn't exist:
    2. git checkout main (git status to validate we are pointing to main)
    3. git pull (to update local main)
    4. ```git checkout -b [feat|bugfix]/[new-branch-name]

4. Work
5. Test
    Dev
    ```bash
    python .\sync_vampires.py dev
    ```
    Pro
    ```bash
    python .\sync_vampires.py pro
    ```
6. git add, commit, push.
7. github: PR main <- [working_branch], merge, delete [working_branch], create new release.