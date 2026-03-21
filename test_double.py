import base64

def test_double_decode(encoded_str):
    # Pad with =
    encoded_str += "=" * (-len(encoded_str) % 4)
    try:
        decoded = base64.urlsafe_b64decode(encoded_str)
        print(f"Decoded Double: {decoded}")
        # Try to decode as utf-8
        try:
            print(f"UTF8: {decoded.decode('utf-8', errors='ignore')}")
        except: pass
    except Exception as e:
        print(f"Error: {e}")

# The AU_yq... part from the binary I saw
au_yq = "AU_yqLN2MigMkCsSqp2gSGPd2mYIrJquffJa4FBG-qdwqHVGedVasAZZmi2CzQMAZCOjB7XEk_1LhHqq7ywgUPJ1tO6KoZEWCKZqEdwNRpTqRPDrxHZIzF0-f7DLep5P3ily4h9J8ynNiwXayfKWMIJduxO-4EReHg"
test_double_decode(au_yq)
