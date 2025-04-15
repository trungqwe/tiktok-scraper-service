from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import re
from dotenv import load_dotenv
from TikTokApi import TikTokApi

# Tải biến môi trường
load_dotenv()

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tiktok-scraper")

app = Flask(__name__)
CORS(app)

# TikTokApi instance cache
api_instance = None

def get_api_instance():
    global api_instance
    if api_instance is None:
        try:
            logger.info("Creating new TikTokApi instance")
            api_instance = TikTokApi()
        except Exception as e:
            logger.error(f"Error creating TikTokApi instance: {e}")
            raise Exception(f"Cannot initialize TikTok API: {str(e)}")
    return api_instance

def convert_count_to_number(text_val):
    """Chuyển đổi chuỗi dạng '1.2K', '3.4M', '123' thành số nguyên"""
    try:
        if isinstance(text_val, (int, float)):
            return int(text_val)
        
        text_val = str(text_val).strip().upper().replace(',', '')
        if 'K' in text_val:
            return int(float(text_val.replace('K', '')) * 1000)
        elif 'M' in text_val:
            return int(float(text_val.replace('M', '')) * 1_000_000)
        else:
            return int(float(text_val))
    except Exception as e:
        logger.error(f"Error converting number: {e}")
        return 0

def verify_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    return token == os.environ.get('AUTH_TOKEN')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "version": "1.0.0"})

@app.route('/scrape', methods=['POST'])
def scrape_tiktok():
    # Verify token
    if not verify_token(request):
        return jsonify({"success": False, "detail": "Invalid authentication"}), 401
    
    # Get request data
    data = request.json
    url = data.get('url')
    
    if not url or '@' not in url:
        return jsonify({"success": False, "detail": "Invalid TikTok URL"}), 400
    
    # Extract username
    username_match = re.search(r'@([^/?]+)', url)
    if not username_match:
        return jsonify({"success": False, "detail": "Could not extract username from URL"}), 400
    
    username = username_match.group(1)
    logger.info(f"Scraping TikTok profile for user: @{username}")
    
    try:
        # Use API instance
        api = get_api_instance()
        
        # Get user info
        user = api.user(username)
        user_info = user.info()
        
        # Get videos
        videos = user.videos(count=30)
        video_list = list(videos)
        
        # Calculate views for 2 most recent videos
        recent_views = 0
        if len(video_list) >= 2:
            for i in range(min(2, len(video_list))):
                if 'stats' in video_list[i] and 'playCount' in video_list[i]['stats']:
                    recent_views += convert_count_to_number(video_list[i]['stats']['playCount'])
        
        # Calculate total views
        total_views = 0
        for video in video_list:
            if 'stats' in video and 'playCount' in video['stats']:
                total_views += convert_count_to_number(video['stats']['playCount'])
        
        # Get followers count
        followers = 0
        if 'stats' in user_info and 'followerCount' in user_info['stats']:
            followers = convert_count_to_number(user_info['stats']['followerCount'])
        
        logger.info(f"Scraped data for @{username}: followers={followers}, recent_views={recent_views}, total_views={total_views}")
        
        return jsonify({
            "success": True,
            "followers": followers,
            "recent_views": recent_views,
            "total_views": total_views
        })
        
    except Exception as e:
        logger.error(f"Error scraping TikTok for @{username}: {str(e)}")
        return jsonify({"success": False, "detail": f"Error scraping TikTok: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
