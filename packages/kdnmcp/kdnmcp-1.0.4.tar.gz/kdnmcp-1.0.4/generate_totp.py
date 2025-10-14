# PKXMIZNT6KBX7EVETKAIAUWJV7LPHPVW
# liuqingling@kdniao.com
# liuqingling
# kdn2025 
# 813249
# kdnmcp
# pypi-AgEIcHlwaS5vcmcCJGNhNjc4NjEyLTc3OTktNGNjZi04NTkwLTQwYjkxZjdkYTNkNAACKlszLCJlNGVjZGFhMy03ODFmLTQyYjUtOGRkNS02YWE5YTM3YjYxNGYiXQAABiCXPu_wMQ9W_MEoq0yDC6sm2cE5x0uD4qlvkjGNTiY1Gw
import pyotp
 
key = 'PKXMIZNT6KBX7EVETKAIAUWJV7LPHPVW'
totp = pyotp.TOTP(key)
print(totp.now())