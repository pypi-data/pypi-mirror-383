# AKIRU-PixelVault

![AKIRU PixelVault Logo](https://images.team-akiru.site/image/upload/v1760018811/user_uploads/68e77c497ba3390f07b75d67/fjjpht18zmuoryid4m0a.png)

**AKIRU-PixelVault** is a Python client library for interacting with the [AKIRU PixelVault API](https://image.api.team-akiru.site). It allows developers and users to **manage images, check storage, upload, list, and delete images** easily using Python.  

The library is designed for simplicity, reliability, and robust error handling.

---

## Table of Contents

<ol>
<li><a href="#installation">Installation</a></li>
<li><a href="#quick-start">Quick Start</a></li>
<li><a href="#usage-examples">Usage Examples</a></li>
<li><a href="#api-reference">API Reference</a></li>
<li><a href="#advanced-usage">Advanced Usage</a></li>
<li><a href="#error-handling">Error Handling</a></li>
<li><a href="#faq">FAQ</a></li>
<li><a href="#license">License</a></li>
<li><a href="#contact">Contact</a></li>
</ol>

---

## Installation

Install the library using `pip`:

```bash
pip install AKIRU-PixelVault
```

Make sure you have Python 3.7 or higher.

# Quick Start

```python
from akiru_pixelvault import PixelVaultClient

client = PixelVaultClient(
    api_key="YOUR_API_KEY",
    user_id="YOUR_USER_ID",
    verbose=True
)

# Check storage
print(client.check_storage())

# List images
print(client.list_images())

# Upload an image
print(client.upload_image("path/to/image.jpg"))

# Delete a specific image
print(client.delete_image("IMAGE_ID"))

# Delete all images
print(client.delete_all_images())
```
---

# Usage Examples

<details>
<summary>Check Storage</summary>storage = client.check_storage()
print("Storage Info:")
print(f"Used: {storage.get('storage_used_readable')}")
print(f"Remaining: {storage.get('bytes_remaining')} bytes")

</details><details>
<summary>List Images</summary>images = client.list_images()
print(f"You have {images.get('count')} images:")
for img in images.get('images', []):
    print(f"- ID: {img['id']}, Size: {img['size_bytes']} bytes")
    print(f"  URL: {img['url']}")

</details><details>
<summary>Upload Image</summary>upload_response = client.upload_image("example.jpg")
if upload_response.get("error"):
    print("Error:", upload_response["error"])
else:
    print("Uploaded successfully:", upload_response["url"])

</details><details>
<summary>Delete Image</summary>delete_response = client.delete_image("IMAGE_ID_HERE")
print(delete_response.get("message"))

</details><details>
<summary>Delete All Images</summary>delete_all_response = client.delete_all_images()
print(delete_all_response.get("message"))

</details>
---

API Reference

<table>
<tr>
<th>Method</th>
<th>Description</th>
<th>Parameters</th>
<th>Returns</th>
</tr><tr>
<td>check_storage()</td>
<td>Get current storage usage and limits.</td>
<td>None</td>
<td>Dict with keys: <code>bytes_remaining</code>, <code>storage_limit_bytes</code>, <code>storage_used_bytes</code>, etc.</td>
</tr><tr>
<td>list_images(limit=None)</td>
<td>Get all uploaded images, optionally limited by <code>limit</code>.</td>
<td><code>limit</code> (int, optional)</td>
<td>Dict with <code>count</code> and <code>images</code> array.</td>
</tr><tr>
<td>upload_image(file_path)</td>
<td>Upload a new image to your account.</td>
<td><code>file_path</code> (str)</td>
<td>Dict with <code>id</code>, <code>url</code>, <code>success</code>.</td>
</tr><tr>
<td>delete_image(image_id)</td>
<td>Delete a specific image by ID.</td>
<td><code>image_id</code> (str)</td>
<td>Dict with <code>message</code> and <code>success</code>.</td>
</tr><tr>
<td>delete_all_images()</td>
<td>Delete all images from the account (use with caution).</td>
<td>None</td>
<td>Dict with <code>message</code> and <code>success</code>.</td>
</tr></table>
---

# Advanced Usage

# Verbose Mode

Enable verbose mode to see debug info for all requests:

```python
client = PixelVaultClient(api_key="KEY", user_id="USER", verbose=True)
```

# Optional Parameters

```python
list_images(limit=10)– fetch only the first 10 images.
```

```python
upload_image(file_path="path/to/file.jpg") – checks if the file exists before upload.
```

---

# Error Handling

All methods return a dictionary. If an error occurs (network, file not found, or API failure), the dictionary contains:

```json
{
    "error": "Error description here"
}
```

# Example:

```python
result = client.upload_image("nonexistent.jpg")
if "error" in result:
    print("Failed:", result["error"])
```

---

FAQ

<details>
<summary>Q: Can I upload multiple images at once?</summary>
A: Currently, `AKIRU-PixelVault` supports uploading **one image at a time**. You can loop over a list of files for batch uploads.
</details><details>
<summary>Q: How do I find my API key and user ID?</summary>
A: Log into your AKIRU account, go to **API Settings**, and copy your credentials.
</details><details>
<summary>Q: Is it safe to delete all images?</summary>
A: Deleting all images is irreversible. Use with caution.
</details>
---

# Contributing

We welcome contributions! Please fork the repository and submit a pull request.
Before submitting, ensure:

Code is PEP8 compliant.

Docstrings and type hints are included.

Unit tests pass (if added).

---

License

MIT License © 2025 Your Name
See the [LICENSE](LICENSE) file for details.


---

# Contact

GitHub: https://github.com/I-SHOW-AKIRU200/AKIRU-PixelVault

Email: akhil600322@gmail.com
