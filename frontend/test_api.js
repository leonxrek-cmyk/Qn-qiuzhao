// 测试API请求的脚本
// 可以在浏览器控制台中运行

console.log('开始测试API请求...');

// 测试获取角色配置的API
fetch('/api/character_config')
  .then(response => {
    console.log('HTTP响应状态:', response.status);
    return response.json().then(data => {
      console.log('API返回的数据:', data);
      if (data && data.success && Array.isArray(data.configs)) {
        console.log(`成功获取到${data.configs.length}个角色配置`);
      } else {
        console.error('API返回的数据格式不正确');
      }
    });
  })
  .catch(error => {
    console.error('API请求失败:', error);
  });