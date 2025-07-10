#!/bin/bash

echo "📁 Navigating to backend directory..."
cd backend || exit 1

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
  echo "🐍 Creating virtual environment..."
  python3 -m venv venv
else
  echo "✅ Virtual environment already exists."
fi

# Activate the virtual environment
echo "⚙️ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check or create .env
if [ ! -f ".env" ]; then
  echo "📝 Creating .env file..."
  cat <<EOF > .env
DHAN_ACCESS_TOKEN=your_token_here
DHAN_CLIENT_ID=your_client_id_here
MAX_INVEST_AMOUNT=10000
EOF
  echo "🔐 Please update your .env file with real credentials."
else
  echo "✅ .env file already exists."
fi

echo "🚀 Setup complete! Run the app with:"
echo ""
echo "   source venv/bin/activate && python app.py"
echo ""