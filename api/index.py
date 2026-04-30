import sys
import os

# Root directory-কে path-এ অ্যাড করা হচ্ছে যাতে main.py রিড করতে পারে
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

# Vercel এই app অবজেক্টটিকেই সার্ভার হিসেবে রান করবে

