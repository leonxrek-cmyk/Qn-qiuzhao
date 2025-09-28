"""
Flask应用主文件 - 重构后的简化版本
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

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
    
    app.register_blueprint(ai_bp, url_prefix='/api')
    app.register_blueprint(character_bp, url_prefix='/api')
    app.register_blueprint(session_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(intimacy_bp, url_prefix='/api')
    
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
