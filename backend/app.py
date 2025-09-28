"""
Flask应用主文件 - 重构后的简化版本
"""
import logging
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

# 配置日志编码，解决Windows下的Unicode问题
if sys.platform.startswith('win'):
    # Windows下强制使用UTF-8编码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/app.log', encoding='utf-8')
        ]
    )

def create_app():
    """创建Flask应用实例"""
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 配置CORS，允许跨域请求
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from routes.ai_routes import ai_bp
    from routes.character_routes import character_bp
    from routes.session_routes import session_bp
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.intimacy_routes import intimacy_bp
    from routes.asr_routes import asr_bp
    from routes.tts_routes import tts_bp
    
    app.register_blueprint(ai_bp, url_prefix='/api')
    app.register_blueprint(character_bp, url_prefix='/api')
    app.register_blueprint(session_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(intimacy_bp, url_prefix='/api')
    app.register_blueprint(asr_bp, url_prefix='/api')
    app.register_blueprint(tts_bp, url_prefix='/api')
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '资源未找到'
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': '请求参数错误'
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=app.config['FLASK_RUN_PORT'],
        debug=app.config['FLASK_ENV'] == 'development'
    )
