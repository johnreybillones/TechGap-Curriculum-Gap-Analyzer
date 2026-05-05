"""
Quick script to find the certificate path used by your Python code.
This path can be used in database IDE extensions for SSL configuration.
"""
import certifi
import os

print("=" * 60)
print("Certificate Path for TiDB SSL Configuration")
print("=" * 60)
print(f"\nCertificate bundle location: {certifi.where()}")
print(f"\nFile exists: {os.path.exists(certifi.where())}")
print("\nYou can use this path as the 'SSL CA File' in your database extension.")
print("\nAlternatively, you can download the CA certificate from TiDB Cloud:")
print("1. Go to TiDB Cloud Console")
print("2. Select your cluster")
print("3. Go to 'Connect' tab")
print("4. Click 'Download CA certificate'")
print("=" * 60)




