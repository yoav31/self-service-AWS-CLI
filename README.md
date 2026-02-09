Platform Engineering Python Exercise:
Automating AWS Resource Provisioning


docker run -it `
  -e AWS_ACCESS_KEY_ID=YOUR_KEY `
  -e AWS_SECRET_ACCESS_KEY=YOUR_SECRET `
  -e AWS_DEFAULT_REGION=us-east-1 `
  my-python-app

# Self-Service AWS CLI

**Self-Service AWS CLI** is a Python command-line interface (CLI) tool for managing AWS resources. The tool provides simple access to S3, EC2, Route53, and more, designed for users who want to perform common AWS operations intuitively.

---

## ⚡ Prerequisites

* Python 3.12+
* Docker (for container version)
* AWS CLI or credentials available 
* Python packages: `boto3`, `click`

---

## 🚀 Installation

### Option 1 – Using Docker (Recommended)

1. Build the image:

```bash
docker build -t my-python-app .
```

2. Run the CLI with access to AWS credentials from your machine:

```bash
docker run -it `
  -e AWS_ACCESS_KEY_ID=YOUR_KEY `
  -e AWS_SECRET_ACCESS_KEY=YOUR_SECRET `
  -e AWS_DEFAULT_REGION=us-east-1 `
  my-python-app
```

---

### Option 2 – Local Environment

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the CLI:

```bash
python main.py
```

---

## 📝 Usage

```bash
python main.py [OPTIONS] COMMAND [ARGS]...
```

Examples:

* **List Hosted Zones (Route53)**

```bash
python main.py route53 list
```

* **List S3 Buckets**

```bash
python main.py s3 list
```

> The tool uses Click to provide clear commands with a `--help` option for each command.

---

## 🌟 Project Structure

```
.
├── Dockerfile
├── requirements.txt
├── main.py
├── S3.py
├── EC2.py
├── Route53.py
├── README.md
└── __pycache__/
```

* **main.py** – CLI entry point
* **S3.py / EC2.py / Route53.py** – modules for managing services
* **Dockerfile** – defines the container image
* **requirements.txt** – required Python packages

---

## ✅ Tips

* Use `docker run -it --entrypoint /bin/sh my-python-app` to inspect the container.
* Ensure AWS credentials are available in `~/.aws` or via environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).
* You can add new commands by creating new Python modules and integrating them into the CLI.

---
