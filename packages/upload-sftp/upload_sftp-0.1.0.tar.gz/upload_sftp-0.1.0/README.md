# SFTP Uploader

A high-performance CLI tool for uploading folders to SFTP servers with async parallel uploads, automatic retries, and progress reporting.

## Features

- 🚀 **Async Parallel Uploads**: Upload multiple files simultaneously for improved performance
- 🔄 **Automatic Retry**: Configurable retry logic with exponential backoff for failed uploads
- 📊 **Progress Tracking**: Real-time progress bar showing upload status
- 📈 **Detailed Reporting**: Summary statistics showing successful, failed, and skipped files
- 🔐 **Flexible Authentication**: Support for password and SSH key authentication
- 🌳 **Recursive Upload**: Maintain directory structure when uploading folders
- ⚙️ **Environment Variables**: Configure settings via environment variables

## Installation

```bash
cd tools/upload-sftp
pip install -e .
```

## Usage

### Basic Usage

```bash
upload-sftp /path/to/local/folder /remote/folder \
    --host sftp.example.com \
    --username myuser \
    --password mypassword
```

### Using SSH Key Authentication

```bash
upload-sftp /path/to/local/folder /remote/folder \
    --host sftp.example.com \
    --username myuser \
    --key-file ~/.ssh/id_rsa
```

### Advanced Options

```bash
upload-sftp /path/to/local/folder /remote/folder \
    --host sftp.example.com \
    --port 2222 \
    --username myuser \
    --password mypassword \
    --max-workers 20 \
    --max-retries 5 \
    --no-recursive
```

### Using Environment Variables

Create a `.env` file or export environment variables:

```bash
export SFTP_HOST=sftp.example.com
export SFTP_PORT=22
export SFTP_USERNAME=myuser
export SFTP_PASSWORD=mypassword
# Or use key file:
# export SFTP_KEY_FILE=~/.ssh/id_rsa
```

Then run without specifying these options:

```bash
upload-sftp /path/to/local/folder /remote/folder
```

## Command-Line Options

| Option | Short | Description | Default | Environment Variable |
|--------|-------|-------------|---------|---------------------|
| `--host` | `-h` | SFTP server hostname | Required | `SFTP_HOST` |
| `--port` | `-p` | SFTP server port | 22 | `SFTP_PORT` |
| `--username` | `-u` | SFTP username | Required | `SFTP_USERNAME` |
| `--password` | | SFTP password | None | `SFTP_PASSWORD` |
| `--key-file` | `-k` | SSH private key file | None | `SFTP_KEY_FILE` |
| `--max-workers` | `-w` | Max parallel uploads | 10 | - |
| `--max-retries` | `-r` | Max retries per file | 3 | - |
| `--recursive` | | Upload recursively | True | - |
| `--no-recursive` | | Don't upload recursively | - | - |

## Example Output

```
Starting SFTP Upload
Local folder: /Users/john/documents
Remote folder: /backup/documents
SFTP host: sftp.example.com:22
Max parallel workers: 10
Max retries per file: 3

Uploading files... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00

Upload Summary
Total files found: 150
Successfully uploaded: 148
Failed: 2
Skipped: 0
Total time: 12.45 seconds

Failed Files:
  • /Users/john/documents/large_file.zip: Connection timeout
  • /Users/john/documents/locked.txt: Permission denied
```

## Performance Tips

1. **Adjust Workers**: Increase `--max-workers` for better performance on fast connections
2. **Network Optimization**: Use servers geographically closer to reduce latency
3. **Retry Configuration**: Adjust `--max-retries` based on network stability
4. **File Size**: Larger files benefit less from parallel uploads

## Error Handling

The tool automatically retries failed uploads with exponential backoff:
- 1st retry: 1 second wait
- 2nd retry: 2 seconds wait
- 3rd retry: 4 seconds wait
- And so on...

Failed uploads are reported at the end with specific error messages.

## Security Notes

⚠️ **Important**: The tool currently disables SSH host key verification for convenience. For production use, consider implementing proper host key verification.

## Requirements

- Python 3.13+
- asyncssh
- typer
- rich

## Development

```bash
# Install in development mode
pip install -e .

# Run directly
python -m upload_sftp.cli --help
```

## License

Part of the LateralCare project.

