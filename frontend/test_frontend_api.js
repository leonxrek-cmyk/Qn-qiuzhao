// 测试前端API连接
document.addEventListener('DOMContentLoaded', async function() {
  console.log('开始测试前端API连接...');
  
  try {
    // 测试获取模型列表
    const modelsResponse = await fetch('/api/models');
    const modelsData = await modelsResponse.json();
    console.log('模型列表API响应:', modelsData);
    console.log('可用模型:', modelsData.models);
    
    // 测试基础聊天API
    const chatResponse = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: '你好，测试连接',
        model: 'x-ai/grok-4-fast'
      })
    });
    const chatData = await chatResponse.json();
    console.log('聊天API响应:', chatData);
    
    // 测试角色扮演聊天API
    const characterChatResponse = await fetch('/api/character_chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        character_name: '测试角色',
        character_description: '这是一个用于测试的角色',
        user_query: '你好，能介绍一下你自己吗？',
        model: 'x-ai/grok-4-fast'
      })
    });
    const characterChatData = await characterChatResponse.json();
    console.log('角色扮演聊天API响应:', characterChatData);
    
    console.log('✅ 所有API测试成功完成！');
  } catch (error) {
    console.error('❌ API测试失败:', error);
  }
});