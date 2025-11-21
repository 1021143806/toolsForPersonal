搜索标题/内容
📖
FlowUs 插件开发完整指南
概述
FlowUs 插件开发系统提供了完整的API接口，允许开发者创建功能丰富的插件来扩展FlowUs的功能。本指南将带您了解从零开始开发插件的完整流程。
插件类型
FlowUs 支持两种不同类型的集成应用，分别适用于不同的开发场景和用户体验需求：
1. 内部插件 (Internal Plugin)
嵌入式UI：插件界面直接嵌入在 FlowUs 应用内部
无缝集成：用户在 FlowUs 内完成所有操作，无需跳转
简化授权：用户在应用内直接选择要授权的页面
适用场景：FlowUs 官方插件、企业内部工具
技术特性：
无需配置 ​​​​redirectUris​​​​
直接API调用操作内容
简化授权流程，一步完成机器人创建和授权
2. 外部应用 (External Application)
独立应用：第三方开发的独立应用程序
标准OAuth2：遵循OAuth2.0授权码流程
跨平台集成：可以在任何平台上开发和部署
适用场景：第三方开发者工具、SaaS服务集成
类型对比表
特性
内部插件 (internal)
外部应用 (external)
spaceId
必填
不需要
redirectUris
可选（通常为空）
必填
机器人创建
创建集成应用时自动创建
需要OAuth2授权流程
页面权限
通过PATCH接口动态管理
OAuth2授权时指定
UI集成
嵌入FlowUs内
独立应用
Token获取
创建时直接返回
OAuth2交换
开发复杂度
简单
中等
安全验证
内部验证
client_secret验证
如何选择类型？
选择内部插件的情况：
开发 FlowUs 官方功能扩展
企业内部工具，不需要对外发布
希望提供无缝的用户体验
不需要复杂的OAuth流程
选择外部应用的情况：
第三方开发者工具
需要在多个平台集成的SaaS服务
独立的应用程序
需要遵循标准OAuth2流程的场景
核心概念
集成应用 (Integration)
插件的基础配置和身份标识
定义插件的基本信息（名称、描述、图标等）
配置OAuth回调地址（公共插件需要）
设置机器人能力权限
开发流程
第一步：创建集成应用
开发者中心主要是提供了一些flowus的api给有开发能力的用户使用，入口在空间设置里。

集成应用主要分2种：
插件内应用：开发者用于自己空间页面，比如想用api对对某个页面进行编辑，就可以创建应用插件。
外部应用：开发者给其他flowus用户使用，比如开发者有一个新闻类网站，希望支持用户把某条新闻同步到flowus，就可以创建外部应用，用户授权后就有相应的权限进行读写。外部应用需要填写自己的网站地址以及callback地址，跟常规网站授权流程差不多。授权后会访问callback地址并且带上可访问用户数据的code。

第二步：应用授权（根据应用类型选择）
内部插件开发流程
内部插件的UI嵌入在FlowUs应用内，创建时直接创建机器人，无需额外的授权步骤。

外部应用开发流程
外部应用是独立的第三方应用，用户在外部应用中操作，通过标准的 OAuth2.0 授权码流程获取权限
访问授权URL
通过访问授权url进入授权页面,选择授权页面后自动跳转调用外部插件配置的重定向URI
重定向URI的接口中用户要添加交换访问令牌逻辑
typescript demo 代码如下
// 在回调页面处理授权码
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');
const state = urlParams.get('state');

// 第三方应用交换访问令牌
const tokenResponse = await fetch('https://api.flowus.cn/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    grant_type: 'authorization_code',
    code: code,
    client_id: integration.id,
    client_secret: integration.secret,
    redirect_uri: 'https://my-plugin.com/callback'
  })
});

const { access_token } = await tokenResponse.json();
完整示例代码
创建页面
// 使用访问令牌调用API
const page = await fetch('https://api.flowus.cn/v1/pages', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    parent: { database_id: 'database-uuid' },
    properties: {
      '标题': {
        type: 'title',
        title: [{ text: { content: '外部应用创建的任务' } }]
      }
    }
  })
});
API 接口总览
OAuth2 授权 API（外部应用）
​​​​GET /oauth/authorize​​​​ - 启动OAuth2授权流程
​​​​GET /oauth/authorize/info​​​​ - 获取授权页面信息
​​​​POST /oauth/token​​​​ - 交换访问令牌
API (v1)
​​​​POST /v1/pages​​​​ - 创建页面/记录
​​​​GET /v1/blocks/{blockId}​​​​ - 获取单个块
​​​​GET /v1/blocks/{blockId}/children​​​​ - 获取块的子块（基于 subNodes 分页）
​​​​PATCH /v1/blocks/{blockId}/children​​​​ - 追加子块到指定块
​​​​PATCH /v1/blocks/{blockId}​​​​ - 更新块
​​​​DELETE /v1/blocks/{blockId}​​​​ - 删除块
分页特性： 子块获取API使用基于父块 ​​​​subNodes​​​​ 字段的分页机制，保持用户设置的块顺序，游标格式为简单的块ID。
机器人API详细说明
认证
所有 API 请求都需要在 HTTP 头中包含 Bearer Token：
Authorization: Bearer your_bot_token_here
基础 URL
正式环境
https://api.flowus.cn/v1
创建页面
创建一个新的页面或多维表记录。
POST /v1/pages
请求体：
{
  "parent": {
    "database_id": "d9824bdc-8445-4327-be8b-5b47500af6ce"
  },
  "icon": {
    "emoji": "📝"
  },
  "cover": {
    "external": {
      "url": "https://example.com/cover.jpg"
    }
  },
  "properties": {
    "标题": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "新页面标题"
          }
        }
      ]
    },
    "描述": {
      "type": "text",
      "text": [
        {
          "text": {
            "content": "页面描述"
          }
        }
      ]
    },
    "状态": {
      "type": "select",
      "select": {
        "name": "进行中"
      }
    },
    "价格": {
      "type": "number",
      "number": 99.99
    }
  }
}
支持的属性类型：
标题属性：
{
  "标题": {
    "type": "title",
    "title": [
      {
        "type": "text",
        "text": {
          "content": "页面标题"
        }
      }
    ]
  }
}
文本属性：
{
  "描述": {
    "type": "text", 
    "text": [
      {
        "type": "text",
        "text": {
          "content": "这是一段描述文本"
        }
      }
    ]
  }
}
选择属性：
{
  "状态": {
    "type": "select",
    "select": {
      "name": "进行中"
    }
  }
}
数字属性：
{
  "价格": {
    "type": "number",
    "number": 99.99
  }
}
权限系统
页面权限管理
机器人只能访问被明确授权的页面
支持动态添加/移除页面权限
权限检查在每次API调用时进行
错误处理
常见错误码
状态码
错误码
描述
错误响应格式
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "请求参数验证失败"
}
说明:
​​​​object​​​​: 固定为 "error"
​​​​status​​​​: HTTP状态码
​​​​code​​​​: 错误类型代码
​​​​message​​​​: 详细错误信息
开发工具和资源
示例代码
// 完整的插件开发示例
class FlowUsPlugin {
  constructor(integrationId, secret) {
    this.integrationId = integrationId;
    this.secret = secret;
    this.accessToken = null;
  }
  
     // OAuth2授权（外部应用）
  async authorize(authCode, redirectUri) {
    const response = await fetch('/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grant_type: 'authorization_code',
        code: authCode,
        client_id: this.integrationId,
        client_secret: this.secret,
        redirect_uri: redirectUri
      })
    });
    
    const data = await response.json();
    this.accessToken = data.access_token;
    return data;
  }
  
  // 创建页面
  async createPage(parentId, properties) {
    const response = await fetch('/v1/pages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        parent: { database_id: parentId },
        properties
      })
    });
    
    return response.json();
  }
}
总结
FlowUs 插件开发系统为不同场景提供了灵活的解决方案：
内部插件：嵌入在FlowUs应用内，用户在软件内完成授权和操作
外部应用：独立的第三方应用，通过REST API与FlowUs集成，遵循标准OAuth2.0流程
选择适合您的应用类型，遵循相应的开发流程，即可快速构建强大的FlowUs集成应用！
快速参考
关键差异对比
特性
内部插件 (internal)
外部应用 (external)
API端点总览
OAuth授权（外部应用）
​​​​GET /oauth/authorize​​​​ - 启动OAuth2授权
​​​​GET /oauth/authorize/info​​​​ - 获取授权页面信息
​​​​POST /oauth/token​​​​ - 交换访问令牌
机器人API (v1)
​​​​POST /v1/pages​​​​ - 创建页面/记录
环境配置
环境
Base URL
描述


搜索标题/内容
🗂️
多维表 API 文档
Database API 提供了对FlowUs多维表（数据库）的完整管理功能，包括创建、查询、检索和更新操作。
概述
Database API 支持以下功能：
创建新的数据库
获取数据库信息
查询数据库记录（支持过滤、排序、分页）
更新数据库配置
认证
所有API请求都需要在Header中包含Bot Token：
Plain Text
1
Authorization: Bearer <your_bot_token>
基础 URL
正式环境
https://api.flowus.cn/v1
测试环境
https://api-test.allflow.cn/v1
数据格式说明
数据格式说明
Database API 使用标准化的数据格式，确保跨平台兼容性：
数据库对象
数据库对象包含以下属性：
{
  "object": "database",
  "id": "uuid",
  "created_time": "2024-01-01T00:00:00.000Z",
  "created_by": {
    "object": "user",
    "id": "uuid"
  },
  "last_edited_time": "2024-01-01T00:00:00.000Z",
  "last_edited_by": {
    "object": "user",
    "id": "uuid"
  },
  "title": [
    {
      "type": "text",
      "text": {
        "content": "数据库标题"
      }
    }
  ],
  "icon": {
    "type": "emoji",
    "emoji": "📋"
  },
  "cover": {
    "type": "external",
    "external": {
      "url": "https://example.com/cover.jpg"
    }
  },
  "properties": {
    "property_id": {
      "id": "property_id",
      "name": "属性名称",
      "type": "property_type"
    }
  },
  "parent": {
    "type": "page_id",
    "page_id": "uuid"
  },
        "url": "https://api.flowus.cn/docs/xxx", // 正式环境
  "archived": false,
  "is_inline": false
}
属性类型
支持的属性类型及其配置：
基础属性类型
title（标题）
{
  "id": "title",
  "name": "标题",
  "type": "title",
  "title": {}
}
rich_text（富文本）
{
  "id": "description",
  "name": "描述",
  "type": "rich_text",
  "rich_text": {}
}
number（数字）
{
  "id": "amount",
  "name": "金额",
  "type": "number",
  "number": {
    "format": "number"
  }
}
checkbox（复选框）
{
  "id": "completed",
  "name": "是否完成",
  "type": "checkbox",
  "checkbox": {}
}
数据格式：
API接受：​​​​{"checkbox": true}​​​​ 或 ​​​​{"checkbox": false}​​​​
date（日期）
{
  "id": "due_date",
  "name": "截止日期",
  "type": "date",
  "date": {}
}
数据格式：
API格式：​​​​{"start": "2024-01-01T10:30:00", "end": null}​​​​
url（链接）
{
  "id": "website",
  "name": "网站",
  "type": "url",
  "url": {}
}
email（邮箱）
{
  "id": "email",
  "name": "邮箱",
  "type": "email",
  "email": {}
}
phone_number（电话）
{
  "id": "phone",
  "name": "电话",
  "type": "phone_number",
  "phone_number": {}
}
选择属性类型
select（单选）
{
  "id": "status",
  "name": "状态",
  "type": "select",
  "select": {
    "options": [
      {
        "id": "option_id",
        "name": "选项名称",
        "color": "blue"
      }
    ]
  }
}
multi_select（多选）
{
  "id": "tags",
  "name": "标签",
  "type": "multi_select",
  "multi_select": {
    "options": [
      {
        "id": "option_id",
        "name": "标签名称",
        "color": "green"
      }
    ]
  }
}
关联属性类型
people（人员）
{
  "id": "assignee",
  "name": "负责人",
  "type": "people",
  "people": {}
}
数据格式：
API格式：​​​​[{"object": "user", "id": "user-uuid"}]​​​​
files（文件）
{
  "id": "attachments",
  "name": "附件",
  "type": "files",
  "files": {}
}
数据格式：
API格式：​​​​[{"name": "file.pdf", "type": "external", "external": {"url": "..."}}]​​​​
relation（关联）
{
  "id": "project",
  "name": "关联项目",
  "type": "relation",
  "relation": {
    "database_id": "related_database_id",
    "synced_property_id": "synced_property_id"
  }
}
rollup（汇总）
{
  "id": "task_count",
  "name": "任务数量",
  "type": "rollup",
  "rollup": {
    "relation_property_id": "relation_property_id",
    "rollup_property_id": "property_to_rollup",
    "function": "count"
  }
}
formula（公式）
{
  "id": "calculated_field",
  "name": "计算字段",
  "type": "formula",
  "formula": {
    "expression": "prop(\"other_property_id\")",
    "version": 2,
    "refProps": {
      "other_property_id": "引用的属性名"
    }
  }
}
注意： Formula属性主要支持读取，创建和更新功能有一定限制。
系统属性类型
created_time（创建时间）
{
  "id": "created_time",
  "name": "创建时间",
  "type": "created_time",
  "created_time": {}
}
created_by（创建者）
{
  "id": "created_by",
  "name": "创建者",
  "type": "created_by",
  "created_by": {}
}
last_edited_time（最后编辑时间）
{
  "id": "last_edited_time",
  "name": "最后编辑时间",
  "type": "last_edited_time",
  "last_edited_time": {}
}
last_edited_by（最后编辑者）
{
  "id": "last_edited_by",
  "name": "最后编辑者",
  "type": "last_edited_by",
  "last_edited_by": {}
}
API 接口
1. 创建数据库
创建一个新的数据库。
POST /v1/databases
请求体
{
  "parent": {
    "type": "page_id",
    "page_id": "string"
  },
  "title": [
    {
      "type": "text",
      "text": {
        "content": "string"
      }
    }
  ],
  "icon": {
    "type": "emoji",
    "emoji": "string"
  },
  "cover": {
    "type": "external",
    "external": {
      "url": "string"
    }
  },
  "properties": {
    "property_id": {
      "id": "string",
      "name": "string",
      "type": "property_type"
    }
  },
  "is_inline": false
}
参数说明
参数
类型
必需
说明
响应
返回创建的数据库对象。
示例
{
  "parent": {
    "type": "page_id",
    "page_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "title": [
    {
      "type": "text",
      "text": {
        "content": "任务管理"
      }
    }
  ],
  "icon": {
    "type": "emoji",
    "emoji": "📋"
  },
  "properties": {
    "title": {
      "id": "title",
      "name": "任务名称",
      "type": "title"
    },
    "status": {
      "id": "status",
      "name": "状态",
      "type": "select",
      "select": {
        "options": [
          {
            "name": "待办",
            "color": "red"
          },
          {
            "name": "进行中",
            "color": "yellow"
          },
          {
            "name": "完成",
            "color": "green"
          }
        ]
      }
    },
    "due_date": {
      "id": "due_date",
      "name": "截止日期",
      "type": "date"
    }
  }
}
2. 获取数据库
获取指定数据库的信息。
GET /v1/databases/{database_id}
路径参数
参数
类型
必需
说明
响应
返回数据库对象。
3. 查询数据库
查询数据库中的记录，支持过滤、排序和分页。
POST /v1/databases/{database_id}/query
路径参数
参数
类型
必需
说明
请求体
{
  "start_cursor": "string",
  "page_size": 50
}
参数说明
参数
类型
必需
说明
响应
{
  "object": "list",
  "results": [
    {
      "object": "page",
      "id": "uuid",
      "created_time": "2024-01-01T00:00:00.000Z",
      "created_by": {
        "object": "user",
        "id": "uuid"
      },
      "last_edited_time": "2024-01-01T00:00:00.000Z",
      "last_edited_by": {
        "object": "user",
        "id": "uuid"
      },
      "archived": false,
      "properties": {
        "title": {
          "id": "title",
          "type": "title",
          "title": [
            {
              "type": "text",
              "text": {
                "content": "任务标题"
              }
            }
          ]
        }
      },
      "parent": {
        "type": "database_id",
        "database_id": "uuid"
      },
      "url": "https://api.flowus.cn/docs/xxx" // 正式环境
    }
  ],
  "next_cursor": "string",
  "has_more": false,
  "type": "page",
  "page": {}
}
4. 更新数据库
更新数据库的配置，包括标题、图标、封面、属性等。
PATCH /v1/databases/{database_id}
路径参数
参数
类型
必需
说明
请求体
{
  "title": [
    {
      "type": "text",
      "text": {
        "content": "string"
      }
    }
  ],
  "icon": {
    "type": "emoji",
    "emoji": "string"
  },
  "cover": {
    "type": "external",
    "external": {
      "url": "string"
    }
  },
  "properties": {
    "property_id": {
      "id": "string",
      "name": "string",
      "type": "property_type"
    }
  },
  "archived": false
}
参数说明
参数
类型
必需
说明
响应
返回更新后的数据库对象。
示例
更新标题和图标
{
  "title": [
    {
      "type": "text",
      "text": {
        "content": "更新后的数据库标题"
      }
    }
  ],
  "icon": {
    "type": "external",
    "external": {
      "url": "https://example.com/new-icon.png"
    }
  }
}
添加新属性
{
  "properties": {
    "assignee": {
      "id": "assignee",
      "name": "负责人",
      "type": "people"
    },
    "estimated_hours": {
      "id": "estimated_hours",
      "name": "预估工时",
      "type": "number"
    }
  }
}
删除属性
{
  "properties": {
    "old_property": null
  }
}
归档数据库
{
  "archived": true
}
数据类型支持
Database API 支持丰富的数据类型，包括：
基础类型：文本、数字、复选框、日期、链接、邮箱、电话
选择类型：单选、多选
关联类型：人员、文件、关联、汇总、公式
系统类型：创建时间、创建者、最后编辑时间、最后编辑者
各种数据类型的详细格式和使用方法请参考上述属性类型说明。
错误处理
API使用标准HTTP状态码返回错误信息：
​​​​400 Bad Request​​​​：请求参数错误
​​​​401 Unauthorized​​​​：认证失败
​​​​403 Forbidden​​​​：权限不足
​​​​404 Not Found​​​​：资源不存在
​​​​500 Internal Server Error​​​​：服务器错误
错误响应格式：
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "详细错误信息"
}
使用限制
每个数据库最多支持100个属性
查询时每页最多返回100条记录
单选和多选属性的选项数量限制为100个
数据库标题最长为100个字符
Formula属性主要支持读取，创建功能可能受限
最佳实践
1
分页查询：对于大型数据库，建议使用适当的页面大小进行分页查询
2
过滤优化：合理使用过滤器减少返回的数据量
3
属性设计：根据实际需求设计数据库属性，避免冗余
4
权限管理：确保机器人具有相应的读写权限
5
错误处理：实现适当的错误处理和重试机制
6
数据处理：正确使用各种数据类型的格式要求
测试建议
1
验证类型转换：测试各种属性类型的创建和查询
2
检查日期格式：确认日期时间的正确格式
3
测试文件上传：验证文件的正确处理
4
复选框功能：测试true/false值的处理
5
Formula属性：验证复杂公式的读取和显示
6
人员属性：测试用户UUID的正确映射
示例用例
任务管理系统
创建一个任务管理数据库：
{
  "parent": {
    "type": "page_id",
    "page_id": "workspace-page-id"
  },
  "title": [
    {
      "type": "text",
      "text": {
        "content": "任务管理"
      }
    }
  ],
  "icon": {
    "type": "emoji",
    "emoji": "✅"
  },
  "properties": {
    "name": {
      "id": "name",
      "name": "任务名称",
      "type": "title"
    },
    "status": {
      "id": "status",
      "name": "状态",
      "type": "select",
      "select": {
        "options": [
          {"name": "待办", "color": "red"},
          {"name": "进行中", "color": "yellow"},
          {"name": "完成", "color": "green"}
        ]
      }
    },
    "assignee": {
      "id": "assignee",
      "name": "负责人",
      "type": "people"
    },
    "due_date": {
      "id": "due_date",
      "name": "截止日期",
      "type": "date"
    },
    "priority": {
      "id": "priority",
      "name": "优先级",
      "type": "select",
      "select": {
        "options": [
          {"name": "低", "color": "green"},
          {"name": "中", "color": "yellow"},
          {"name": "高", "color": "red"}
        ]
      }
    }
  }
}
客户关系管理
创建一个CRM数据库：
{
  "parent": {
    "type": "page_id",
    "page_id": "crm-page-id"
  },
  "title": [
    {
      "type": "text",
      "text": {
        "content": "客户管理"
      }
    }
  ],
  "properties": {
    "company": {
      "id": "company",
      "name": "公司名称",
      "type": "title"
    },
    "contact_person": {
      "id": "contact_person",
      "name": "联系人",
      "type": "rich_text"
    },
    "email": {
      "id": "email",
      "name": "邮箱",
      "type": "email"
    },
    "phone": {
      "id": "phone",
      "name": "电话",
      "type": "phone_number"
    },
    "website": {
      "id": "website",
      "name": "网站",
      "type": "url"
    },
    "industry": {
      "id": "industry",
      "name": "行业",
      "type": "select",
      "select": {
        "options": [
          {"name": "科技", "color": "blue"},
          {"name": "金融", "color": "green"},
          {"name": "教育", "color": "yellow"},
          {"name": "医疗", "color": "red"}
        ]
      }
    },
    "deal_stage": {
      "id": "deal_stage",
      "name": "成交阶段",
      "type": "select",
      "select": {
        "options": [
          {"name": "潜在客户", "color": "gray"},
          {"name": "初步接触", "color": "yellow"},
          {"name": "需求确认", "color": "orange"},
          {"name": "方案制定", "color": "blue"},
          {"name": "合同谈判", "color": "purple"},
          {"name": "成交", "color": "green"}
        ]
      }
    }
  }
}
搜索标题/内容
📙
页面多维表属性
概述
Page Properties 定义了页面和数据库记录的属性格式。本文档详细说明了不同类型属性的数据结构、使用方法和格式要求。
页面属性广泛应用于：
页面标题：普通页面的标题属性
数据库记录：多维表中记录的各种属性
页面元数据：图标、封面、创建时间等
基础概念
属性对象结构
每个属性对象都包含以下基本字段：
JSON
1
{
2
  "属性名称": {
3
    "id": "属性UUID",
4
    "type": "属性类型",
5
    "属性类型": "属性值"
6
  }
7
}
字段说明：
​​​​属性名称​​​​：用户可读的属性名称，作为对象的key
​​​​id​​​​：属性的唯一标识符（UUID）
​​​​type​​​​：属性类型，定义了数据的格式和行为
​​​​属性类型​​​​：与type字段相同的key，包含实际的属性值
支持的属性类型
FlowUs 支持 15 种不同的属性类型，涵盖了从基础数据到复杂关联的所有需求：
基础属性类型
​​​​title​​​​ - 标题属性
​​​​rich_text​​​​ - 富文本属性
​​​​number​​​​ - 数字属性
​​​​checkbox​​​​ - 复选框属性
​​​​url​​​​ - 链接属性
​​​​email​​​​ - 邮箱属性
​​​​phone_number​​​​ - 电话属性
选择属性类型
​​​​select​​​​ - 单选下拉框
​​​​multi_select​​​​ - 多选下拉框
时间和人员属性
​​​​date​​​​ - 日期时间属性
​​​​people​​​​ - 人员属性
文件和关联属性
​​​​files​​​​ - 文件附件属性
​​​​relation​​​​ - 数据库关联属性
计算属性类型（只读）
​​​​formula​​​​ - 公式计算属性
1. 标题属性 (title)
页面和数据库记录的主标题。
API格式：
{
  "标题": {
    "id": "title",
    "type": "title",
    "title": [
      {
        "type": "text",
        "text": {
          "content": "页面标题内容",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "页面标题内容",
        "href": null
      }
    ]
  }
}
创建/更新时的简化格式：
{
  "标题": {
    "type": "title",
    "title": [
      {
        "text": {
          "content": "页面标题内容"
        }
      }
    ]
  }
}
2. 富文本属性 (rich_text)
支持格式化的文本内容。
API格式：
{
  "描述": {
    "id": "property-uuid",
    "type": "rich_text",
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "这是一段富文本",
          "link": null
        },
        "annotations": {
          "bold": true,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "blue"
        },
        "plain_text": "这是一段富文本",
        "href": null
      }
    ]
  }
}
创建/更新时的格式：
{
  "描述": {
    "type": "rich_text",
    "rich_text": [
      {
        "text": {
          "content": "这是一段富文本"
        }
      }
    ]
  }
}
3. 数字属性 (number)
数值类型的属性。
API格式：
{
  "价格": {
    "id": "price-uuid",
    "type": "number",
    "number": 99.99
  }
}
创建/更新时的格式：
{
  "价格": {
    "type": "number",
    "number": 99.99
  }
}
4. 选择属性 (select)
单选下拉框属性。
API格式：
{
  "状态": {
    "id": "status-uuid",
    "type": "select",
    "select": {
      "id": "option-uuid",
      "name": "进行中",
      "color": "yellow"
    }
  }
}
创建/更新时的格式：
{
  "状态": {
    "type": "select",
    "select": {
      "name": "进行中"
    }
  }
}
5. 多选属性 (multi_select)
多选下拉框属性。
API格式：
{
  "标签": {
    "id": "tags-uuid",
    "type": "multi_select",
    "multi_select": [
      {
        "id": "tag1-uuid",
        "name": "重要",
        "color": "red"
      },
      {
        "id": "tag2-uuid",
        "name": "紧急",
        "color": "orange"
      }
    ]
  }
}
创建/更新时的格式：
{
  "标签": {
    "type": "multi_select",
    "multi_select": [
      {
        "name": "重要"
      },
      {
        "name": "紧急"
      }
    ]
  }
}
6. 复选框属性 (checkbox)
布尔值属性。
API格式：
{
  "完成": {
    "id": "completed-uuid",
    "type": "checkbox",
    "checkbox": true
  }
}
创建/更新时的格式：
{
  "完成": {
    "type": "checkbox",
    "checkbox": true
  }
}
7. 日期属性 (date)
日期和时间属性。
API格式：
{
  "截止日期": {
    "id": "due-date-uuid",
    "type": "date",
    "date": {
      "start": "2024-01-15T10:30:00",
      "end": "2024-01-16T18:00:00",
      "time_zone": null
    }
  }
}
创建/更新时的格式：
{
  "截止日期": {
    "type": "date",
    "date": {
      "start": "2024-01-15T10:30:00",
      "end": "2024-01-16T18:00:00"
    }
  }
}
日期格式说明：
​​​​start​​​​：开始日期时间（必填）
​​​​end​​​​：结束日期时间（可选）
支持格式：
日期：​​​​YYYY-MM-DD​​​​
日期时间：​​​​YYYY-MM-DDTHH:MM:SS​​​​
带时区：​​​​YYYY-MM-DDTHH:MM:SS+08:00​​​​
8. 人员属性 (people)
用户引用属性。
API格式：
{
  "负责人": {
    "id": "assignee-uuid",
    "type": "people",
    "people": [
      {
        "object": "user",
        "id": "user-uuid"
      }
    ]
  }
}
创建/更新时的格式：
{
  "负责人": {
    "type": "people",
    "people": [
      {
        "id": "user-uuid"
      }
    ]
  }
}
9. 文件属性 (files)
文件附件属性。
API格式：
{
  "附件": {
    "id": "files-uuid",
    "type": "files",
    "files": [
      {
        "name": "文档.pdf",
        "type": "external",
        "external": {
          "url": "https://example.com/document.pdf"
        }
      },
      {
        "name": "图片.jpg",
        "type": "file",
        "file": {
          "url": "https://api.flowus.cn/oss/image.jpg",
          "expiry_time": "2024-01-15T10:30:00.000Z"
        }
      }
    ]
  }
}
创建/更新时的格式：
{
  "附件": {
    "type": "files",
    "files": [
      {
        "name": "文档.pdf",
        "external": {
          "url": "https://example.com/document.pdf"
        }
      }
    ]
  }
}
10. 链接属性 (url)
URL链接属性。
API格式：
{
  "网站": {
    "id": "url-uuid",
    "type": "url",
    "url": "https://example.com"
  }
}
创建/更新时的格式：
{
  "网站": {
    "type": "url",
    "url": "https://example.com"
  }
}
11. 邮箱属性 (email)
邮箱地址属性。
API格式：
{
  "联系邮箱": {
    "id": "email-uuid",
    "type": "email",
    "email": "contact@example.com"
  }
}
创建/更新时的格式：
{
  "联系邮箱": {
    "type": "email",
    "email": "contact@example.com"
  }
}
12. 电话属性 (phone_number)
电话号码属性。
API格式：
{
  "联系电话": {
    "id": "phone-uuid",
    "type": "phone_number",
    "phone_number": "+86 138-0013-8000"
  }
}
创建/更新时的格式：
{
  "联系电话": {
    "type": "phone_number",
    "phone_number": "+86 138-0013-8000"
  }
}
13. 关联属性 (relation)
关联到其他数据库记录的属性。
API格式：
{
  "关联项目": {
    "id": "relation-uuid",
    "type": "relation",
    "relation": [
      {
        "id": "related-page-uuid-1"
      },
      {
        "id": "related-page-uuid-2"
      }
    ],
    "has_more": false
  }
}
创建/更新时的格式：
{
  "关联项目": {
    "type": "relation",
    "relation": [
      {
        "id": "related-page-uuid-1"
      },
      {
        "id": "related-page-uuid-2"
      }
    ]
  }
}
特殊说明：
​​​​relation​​​​ 数组包含关联的页面ID
​​​​has_more​​​​ 表示是否还有更多关联项（分页）
关联的页面必须在指定的目标数据库中
双向关联会自动在目标记录中创建反向关联
14. 公式属性 (formula)
基于其他属性计算得出的只读属性。
API格式：
{
  "总价": {
    "id": "formula-uuid",
    "type": "formula",
    "formula": {
      "type": "number",
      "number": 15000,
      "string": null
    }
  }
}
数据库配置时的格式：
{
  "总价": {
    "type": "formula",
    "formula": {
      "expression": "prop(\"单价\") * prop(\"数量\")",
      "version": 2,
      "refProps": {
        "单价": "price-property-uuid",
        "数量": "quantity-property-uuid"
      }
    }
  }
}
特殊说明：
公式属性是只读的，不能直接修改
​​​​formula.type​​​​ 可能是 ​​​​number​​​​、​​​​string​​​​、​​​​boolean​​​​ 或 ​​​​date​​​​
​​​​formula.expression​​​​ 定义了计算表达式
​​​​refProps​​​​ 包含公式中引用的其他属性映射
计算结果根据引用属性的变化自动更新
常见公式表达式：
数学运算：​​​​prop("价格") * prop("数量")​​​​
字符串连接：​​​​prop("姓") + " " + prop("名")​​​​
条件判断：​​​​if(prop("完成"), "已完成", "未完成")​​​​
日期计算：​​​​dateBetween(prop("结束日期"), prop("开始日期"), "days")​​​​
汇总函数类型：
​​​​count​​​​ - 计数
​​​​count_values​​​​ - 非空值计数
​​​​empty​​​​ - 空值计数
​​​​not_empty​​​​ - 非空值计数
​​​​sum​​​​ - 求和
​​​​average​​​​ - 平均值
​​​​min​​​​ - 最小值
​​​​max​​​​ - 最大值
​​​​range​​​​ - 范围（最大值-最小值）
特殊说明：
汇总属性是只读的，基于关联记录自动计算
​​​​relation_property_id​​​​ 指定要汇总的关联属性
​​​​rollup_property_id​​​​ 指定关联记录中要汇总的目标属性
​​​​array​​​​ 包含所有参与汇总的原始值
系统属性
以下属性由系统自动管理，只读不可修改：
创建时间 (created_time)
{
  "创建时间": {
    "id": "created_time",
    "type": "created_time",
    "created_time": "2024-01-15T10:30:00.000Z"
  }
}
创建者 (created_by)
{
  "创建者": {
    "id": "created_by",
    "type": "created_by",
    "created_by": {
      "object": "user",
      "id": "user-uuid"
    }
  }
}
最后编辑时间 (last_edited_time)
{
  "最后编辑时间": {
    "id": "last_edited_time",
    "type": "last_edited_time",
    "last_edited_time": "2024-01-15T10:35:00.000Z"
  }
}
最后编辑者 (last_edited_by)
{
  "最后编辑者": {
    "id": "last_edited_by",
    "type": "last_edited_by",
    "last_edited_by": {
      "object": "user",
      "id": "user-uuid"
    }
  }
}
使用示例
创建页面时设置属性
POST /v1/pages
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "parent": {
    "database_id": "database-uuid"
  },
  "properties": {
    "标题": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "新项目计划"
          }
        }
      ]
    },
    "状态": {
      "type": "select",
      "select": {
        "name": "计划中"
      }
    },
    "优先级": {
      "type": "select",
      "select": {
        "name": "高"
      }
    },
    "完成": {
      "type": "checkbox",
      "checkbox": false
    },
    "开始日期": {
      "type": "date",
      "date": {
        "start": "2024-01-15"
      }
    },
    "负责人": {
      "type": "people",
      "people": [
        {
          "id": "user-uuid"
        }
      ]
    },
    "预算": {
      "type": "number",
      "number": 50000
    },
    "描述": {
      "type": "rich_text",
      "rich_text": [
        {
          "text": {
            "content": "这是一个重要的项目计划"
          }
        }
      ]
    }
  }
}
更新页面属性
PATCH /v1/pages/page-uuid
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "properties": {
    "状态": {
      "type": "select",
      "select": {
        "name": "进行中"
      }
    },
    "完成": {
      "type": "checkbox",
      "checkbox": true
    },
    "实际预算": {
      "type": "number",
      "number": 45000
    }
  }
}
复杂属性示例
{
  "properties": {
    "项目标题": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "FlowUs API 集成项目"
          }
        }
      ]
    },
    "项目描述": {
      "type": "rich_text",
      "rich_text": [
        {
          "text": {
            "content": "开发 FlowUs API 集成功能，包括："
          }
        },
        {
          "text": {
            "content": "\n1. 页面管理API"
          }
        },
        {
          "text": {
            "content": "\n2. 数据库操作API"
          }
        },
        {
          "text": {
            "content": "\n3. 权限管理系统"
          }
        }
      ]
    },
    "项目标签": {
      "type": "multi_select",
      "multi_select": [
        {
          "name": "API开发"
        },
        {
          "name": "后端"
        },
        {
          "name": "集成"
        }
      ]
    },
    "项目时间": {
      "type": "date",
      "date": {
        "start": "2024-01-01T09:00:00",
        "end": "2024-03-31T18:00:00"
      }
    },
    "团队成员": {
      "type": "people",
      "people": [
        {
          "id": "user1-uuid"
        },
        {
          "id": "user2-uuid"
        }
      ]
    },
         "项目文档": {
       "type": "files",
       "files": [
         {
           "name": "API设计文档.pdf",
           "external": {
             "url": "https://example.com/api-design.pdf"
           }
         },
         {
           "name": "技术规格书.docx",
           "external": {
             "url": "https://example.com/tech-spec.docx"
           }
         }
       ]
     },
     "关联客户": {
       "type": "relation",
       "relation": [
         {
           "id": "customer-uuid-1"
         },
         {
           "id": "customer-uuid-2"
         }
       ]
     },
     "项目进度": {
       "type": "formula",
       "formula": {
         "expression": "if(prop(\"完成任务数\") > 0, prop(\"完成任务数\") / prop(\"总任务数\") * 100, 0)"
       }
     }
  }
}
属性验证规则
必填属性
title: 在创建页面时，至少需要一个title类型的属性
数据库记录: 必须符合数据库schema中定义的属性结构
格式验证
日期格式: 必须符合ISO 8601标准
邮箱格式: 必须是有效的邮箱地址格式
URL格式: 必须是有效的HTTP/HTTPS URL
数字范围: 支持整数和浮点数，精度最多15位
长度限制
文本内容: 单个富文本块最大2000字符
选项名称: 最大100字符
URL长度: 最大2000字符
文件名: 最大255字符
注意事项
属性名称映射
API使用用户可读的属性名称作为key
内部存储使用UUID作为属性标识符
创建时只需提供属性名称，系统自动生成UUID
数据库属性约束
页面属性必须符合所属数据库的schema定义
选择类型的值必须是数据库中预定义的选项
关联属性需要引用有效的记录ID，且目标记录必须在指定的数据库中
公式属性是只读的，不能通过API直接修改，只能在数据库schema中配置
汇总属性依赖于关联属性，需要先建立正确的关联关系
公式和汇总属性的计算结果会随着引用数据的变化自动更新
性能建议
批量操作时，建议每次最多更新50个属性
大型富文本内容建议分段处理
文件属性建议使用外部链接而非上传
错误处理
常见错误
​​​​400 Bad Request​​​​: 属性格式不正确
​​​​403 Forbidden​​​​: 没有修改属性的权限
​​​​404 Not Found​​​​: 引用的属性或关联对象不存在
​​​​422 Unprocessable Entity​​​​: 属性值不符合数据库schema
错误示例
选择属性值错误：
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "属性'状态'的值'无效状态'不在允许的选项列表中"
}
关联属性错误：
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "关联属性'关联项目'引用的记录 'invalid-uuid' 不存在于目标数据库中"
}
尝试修改只读属性：
{
  "object": "error",
  "status": 400,
  "code": "read_only_property",
  "message": "公式属性'总价'是只读的，不能直接修改"
}
公式表达式错误：
{
  "object": "error", 
  "status": 400,
  "code": "formula_error",
  "message": "公式表达式语法错误：无法解析 'prop(\"不存在的属性\")'"
}
相关文档
Pages API 文档 - 页面操作接口
Database API 文档 - 数据库操作接口
Block Objects 文档 - 富文本对象详细格式
搜索标题/内容
📘
页面 API 文档
概述
Pages API 提供了完整页面管理能力，包括：
创建页面：在页面或数据库中创建新页面
获取页面：根据ID获取页面详细信息
更新页面：修改页面属性、图标、封面等
获取页面子块：获取页面的子块列表（支持分页和递归）
支持在普通页面下创建子页面，也支持在数据库中创建记录页面。
基础 URL
正式环境
Plain Text
1
https://api.flowus.cn/v1
测试环境
https://api-test.allflow.cn/v1
认证
所有 API 请求都需要在 Authorization 头中包含有效的机器人令牌：
Authorization: Bearer <bot_token>
API 接口
1. 创建页面
创建新的页面。
请求
POST /v1/pages
请求体
{
  "parent": {
    "page_id": "父页面ID",
    "database_id": "数据库ID"
  },
  "icon": {
    "emoji": "📄",
    "external": {
      "url": "图标URL"
    }
  },
  "cover": {
    "external": {
      "url": "封面URL"
    }
  },
  "properties": {
    "title": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "页面标题"
          }
        }
      ]
    }
  }
}
参数说明：
参数
类型
必填
描述
默认父级： 当不指定 ​​​​parent​​​​ 时，页面将创建在默认位置，您可以在工作区中找到并管理这些页面。
容错机制： 当指定的 ​​​​parent.page_id​​​​ 或 ​​​​parent.database_id​​​​ 不存在时，API会使用默认位置创建页面，确保创建操作能够成功完成。
响应
{
  "object": "page",
  "id": "页面ID",
  "created_time": "2023-12-01T10:00:00.000Z",
  "created_by": {
    "object": "user",
    "id": "用户ID"
  },
  "last_edited_time": "2023-12-01T10:00:00.000Z",
  "last_edited_by": {
    "object": "user",
    "id": "用户ID"
  },
  "archived": false,
  "properties": {
    "title": {
      "id": "title",
      "type": "title",
      "title": [
        {
          "type": "text",
          "text": {
            "content": "页面标题"
          }
        }
      ]
    }
  },
  "parent": {
    "type": "page_id",
    "page_id": "父页面ID"
  },
  "url": "https://api.flowus.cn/docs/页面ID" // 正式环境
}
2. 获取页面
根据页面ID获取页面详细信息。
请求
GET /v1/pages/{page_id}
路径参数
​​​​page_id​​​​: 页面ID
响应
{
  "object": "page",
  "id": "页面ID",
  "created_time": "2023-12-01T10:00:00.000Z",
  "created_by": {
    "object": "user",
    "id": "创建者ID"
  },
  "last_edited_time": "2023-12-01T10:00:00.000Z",
  "last_edited_by": {
    "object": "user",
    "id": "编辑者ID"
  },
  "archived": false,
  "properties": {
    "title": {
      "id": "title",
      "type": "title",
      "title": [
        {
          "type": "text",
          "text": {
            "content": "页面标题"
          }
        }
      ]
    },
    "描述": {
      "id": "property-uuid",
      "type": "rich_text",
      "rich_text": [
        {
          "type": "text",
          "text": {
            "content": "页面描述内容"
          }
        }
      ]
    }
  },
  "parent": {
    "type": "page_id",
    "page_id": "父页面ID"
  },
  "url": "https://api.flowus.cn/docs/页面ID",
  "icon": {
    "type": "emoji",
    "emoji": "📝"
  },
  "cover": {
    "type": "external",
    "external": {
      "url": "https://example.com/cover.jpg"
    }
  }
}
3. 更新页面
更新页面的属性、图标、封面或归档状态。
请求
PATCH /v1/pages/{page_id}
路径参数
​​​​page_id​​​​: 页面ID
请求体
{
  "properties": {
    "title": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "更新后的标题"
          }
        }
      ]
    },
    "描述": {
      "type": "rich_text",
      "rich_text": [
        {
          "text": {
            "content": "更新后的描述"
          }
        }
      ]
    },
    "状态": {
      "type": "select",
      "select": {
        "name": "已完成"
      }
    }
  },
  "icon": {
    "emoji": "✅"
  },
  "cover": {
    "external": {
      "url": "https://example.com/new-cover.jpg"
    }
  },
  "archived": false
}
响应
{
  "object": "page",
  "id": "页面ID",
  "created_time": "2023-12-01T10:00:00.000Z",
  "created_by": {
    "object": "user",
    "id": "创建者ID"
  },
  "last_edited_time": "2023-12-01T10:30:00.000Z",
  "last_edited_by": {
    "object": "user",
    "id": "编辑者ID"
  },
  "archived": false,
  "properties": {
    // 更新后的属性
  },
  "parent": {
    "type": "page_id",
    "page_id": "父页面ID"
  },
  "url": "https://api.flowus.cn/docs/页面ID",
  "icon": {
    "type": "emoji",
    "emoji": "✅"
  },
  "cover": {
    "type": "external",
    "external": {
      "url": "https://example.com/new-cover.jpg"
    }
  }
}
4. 获取页面子块
获取指定页面的子块列表。
请求
GET /v1/blocks/{pageId}/children
重要说明： 页面在 FlowUs 中是特殊的块对象，因此使用 Blocks API 的子块获取接口。
查询参数
​​​​page_size​​​​ (可选): 每页返回的块数量，最大100，默认50
​​​​start_cursor​​​​ (可选): 分页游标，使用子块的ID作为游标值
​​​​recursive​​​​ (可选): 是否递归获取所有子块，​​​​true​​​​或​​​​false​​​​，默认​​​​false​​​​
响应
{
  "object": "list",
  "results": [
    {
      "object": "block",
      "id": "块ID",
      "created_time": "2023-12-01T10:00:00.000Z",
      "created_by": {
        "object": "user",
        "id": "用户ID"
      },
      "last_edited_time": "2023-12-01T10:00:00.000Z",
      "last_edited_by": {
        "object": "user",
        "id": "用户ID"
      },
      "archived": false,
      "has_children": true,
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "文本内容",
              "link": null
            },
            "annotations": {
              "bold": false,
              "italic": false,
              "strikethrough": false,
              "underline": false,
              "code": false,
              "color": "default"
            },
            "plain_text": "文本内容",
            "href": null
          }
        ],
        "color": "default"
      }
    }
  ],
  "next_cursor": "abc-123-def-456",
  "has_more": true,
  "type": "block",
  "block": {},
  "page": {
    "id": "页面ID",
    "title": "页面标题"
  },
  "total_count": null,
  "pagination_info": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 125
  }
}
页面属性格式
页面属性定义了页面和数据库记录的所有属性类型和格式。详细的属性结构、数据类型、使用方法等信息，请参考：
​​📖​​ Page Properties 文档
该文档包含了完整的属性规范：
基础属性 - title、rich_text、number、checkbox等
选择属性 - select、multi_select等下拉框类型
关联属性 - people、files、date等复杂类型
系统属性 - created_time、created_by等只读属性
格式要求 - 各种属性类型的数据格式和验证规则
使用示例 - 创建和更新属性的完整示例
富文本对象格式
API 返回的富文本对象遵循统一的格式规范。详细的富文本对象结构、支持的块类型、颜色定义等信息，请参考：
​​📖​​ Block 对象实体文档
该文档包含了完整的规范说明：
富文本 (RichText) - 文本、提及、公式等类型的详细格式
注解 (Annotations) - 粗体、斜体、颜色等格式化选项
支持的块类型 - 所有可用的块类型及其属性
颜色定义 - 完整的颜色值列表
图标格式 - Emoji、文件、外部链接图标
日期格式 - 各种日期时间格式的支持
使用示例
获取页面的直接子块（游标分页 - 推荐）
注意： 页面在 FlowUs 中也是一种块对象，因此获取页面的子块需要使用 Blocks API。
# 第一页
GET /v1/blocks/abc123/children?page_size=10
Authorization: Bearer your_bot_token

# 使用返回的 next_cursor 获取下一页
GET /v1/blocks/abc123/children?page_size=10&start_cursor=abc-123-def-456
Authorization: Bearer your_bot_token
API 参考： 详细的子块获取说明请参考 Blocks API 文档。
创建新页面
POST /v1/pages
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "parent": {
    "page_id": "parent-page-id"
  },
  "properties": {
    "title": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "新页面标题"
          }
        }
      ]
    }
  }
}
创建页面（无需指定父级）
创建页面时可以不指定父级，页面将创建在默认位置：
POST /v1/pages
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "properties": {
    "title": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "生成的会议纪要"
          }
        }
      ]
    },
    "内容": {
      "type": "rich_text",
      "rich_text": [
        {
          "text": {
            "content": "生成的内容"
          }
        }
      ]
    }
  },
  "icon": {
    "emoji": "🤖"
  }
}
获取页面详情
GET /v1/pages/abc123
Authorization: Bearer your_bot_token
更新页面
PATCH /v1/pages/abc123
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "properties": {
    "title": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "更新后的页面标题"
          }
        }
      ]
    },
    "描述": {
      "type": "rich_text",
      "rich_text": [
        {
          "text": {
            "content": "这是更新后的页面描述"
          }
        }
      ]
    }
  },
  "icon": {
    "emoji": "✅"
  },
  "archived": false
}
创建数据库页面
在数据库中创建新页面（记录）：
POST /v1/pages
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "parent": {
    "database_id": "database-uuid"
  },
  "properties": {
    "标题": {
      "type": "title",
      "title": [
        {
          "text": {
            "content": "新任务"
          }
        }
      ]
    },
    "状态": {
      "type": "select",
      "select": {
        "name": "进行中"
      }
    },
    "优先级": {
      "type": "select",
      "select": {
        "name": "高"
      }
    },
    "完成": {
      "type": "checkbox",
      "checkbox": false
    },
    "截止日期": {
      "type": "date",
      "date": {
        "start": "2024-01-15"
      }
    }
  }
}
批量更新页面属性
PATCH /v1/pages/abc123
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "properties": {
    "状态": {
      "type": "select",
      "select": {
        "name": "已完成"
      }
    },
    "完成": {
      "type": "checkbox",
      "checkbox": true
    },
    "完成时间": {
      "type": "date",
      "date": {
        "start": "2024-01-10T14:30:00"
      }
    }
  },
  "archived": false
}
基于 subNodes 的分页机制
FlowUs 使用基于父块 ​​​​subNodes​​​​ 字段的分页机制，保持用户设置的块顺序：
游标格式
start_cursor = "block_id"
例如: "abc-123-def-456"
工作原理
1
保持用户排序: 严格按照父块 ​​​​subNodes​​​​ 字段中的顺序返回子块
2
简单游标: 使用子块ID作为游标，简单易用
3
高效查询: 基于数组索引进行分页，性能优异
4
顺序一致: 确保返回的子块顺序与用户在界面中看到的一致
分页逻辑
1
从父块的 ​​​​subNodes​​​​ 数组中获取子块ID列表
2
根据 ​​​​start_cursor​​​​ 在数组中找到起始位置
3
使用数组切片获取当前页的子块ID
4
批量查询子块详细信息并过滤权限
5
返回结果和下一页游标
分页特性
直接子块查询（非递归）
基于 subNodes: 使用父块的 ​​​​subNodes​​​​ 字段进行分页
优势:
保持用户设置的块顺序
高效的数组索引操作
简单直观的块ID游标
即使有新数据插入也保持顺序一致性
递归子块查询
偏移分页: 使用偏移量进行分页
包含总数: 返回准确的分页信息
递归深度限制: 最大50层，防止无限递归
使用建议
1
优先使用非递归模式：适合大部分场景，保持用户排序
2
合理设置页面大小：建议20-50条，最大不超过100条
3
使用简单游标：基于块ID的游标更直观易用
错误处理
API 会返回标准的HTTP状态码和错误信息：
常见错误码
​​​​400 Bad Request​​​​: 请求参数错误
缺少必需的 ​​​​parent​​​​ 参数
​​​​properties​​​​ 格式不正确
图标或封面URL格式无效
父级类型与属性不匹配（如在普通页面中使用数据库属性）
​​​​401 Unauthorized​​​​: 认证失败
缺少 ​​​​Authorization​​​​ 头
Token格式错误或已过期
机器人Token无效
​​​​403 Forbidden​​​​: 权限不足
机器人缺少所需能力（如 ​​​​insertContent​​​​、​​​​updateContent​​​​）
机器人没有访问目标页面的权限
尝试操作未授权的页面或数据库
​​​​404 Not Found​​​​: 资源不存在
页面ID不存在
父级页面或数据库不存在（容错：API会使用默认位置创建页面）
引用的属性或关系对象不存在
​​​​500 Internal Server Error​​​​: 服务器错误
页面创建或更新失败
操作执行失败
权限验证失败
错误响应格式
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "请求参数验证失败：缺少必需的parent参数"
}
特定场景错误示例
创建页面错误
// 缺少parent参数
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "必须指定parent.database_id或parent.page_id"
}

// 机器人能力不足
{
  "object": "error",
  "status": 403,
  "code": "forbidden",
  "message": "机器人缺少insertContent能力"
}
获取页面错误
// 页面不存在
{
  "object": "error",
  "status": 404,
  "code": "not_found",
  "message": "页面不存在"
}

// 权限不足
{
  "object": "error",
  "status": 403,
  "code": "forbidden",
  "message": "机器人没有访问此页面的权限"
}
更新页面错误
// 属性类型不匹配
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "属性类型不匹配：期待title类型，收到text类型"
}

// 机器人能力不足
{
  "object": "error",
  "status": 403,
  "code": "forbidden",
  "message": "机器人缺少updateContent能力"
}
搜索标题/内容
📗
块对象实体
概述
本文档详细描述了 FlowUs Blocks API 中所有块类型的对象结构、属性定义和数据格式。每个块对象都包含通用属性和特定于块类型的属性。
通用块对象结构
所有块对象都包含以下通用属性：
JSON
1
{
2
  "object": "block",
3
  "id": "string",
4
  "parent": {
5
    "type": "block_id" | "page_id" | "workspace",
6
    "block_id"?: "string",
7
    "page_id"?: "string"
8
  },
9
  "created_time": "string (ISO 8601)",
10
  "created_by": {
11
    "object": "user",
12
    "id": "string"
13
  },
14
  "last_edited_time": "string (ISO 8601)",
15
  "last_edited_by": {
16
    "object": "user", 
17
    "id": "string"
18
  },
19
  "archived": "boolean",
20
  "has_children": "boolean",
21
  "type": "string",
22
  "data": {
23
    // 特定于块类型的属性
24
  }
25
}
通用属性说明
属性
类型
描述
​​​​object​​​​
​​​​string​​​​
固定值 ​​​​"block"​​​​
​​​​id​​​​
​​​​string​​​​
块的唯一标识符 (UUID)
​​​​parent​​​​
​​​​object​​​​
父级对象信息
​​​​created_time​​​​
​​​​string​​​​
创建时间 (ISO 8601 格式)
​​​​created_by​​​​
​​​​object​​​​
创建者信息
​​​​last_edited_time​​​​
​​​​string​​​​
最后编辑时间 (ISO 8601 格式)
父级对象 (Parent Object)
type Parent = {
  type: "block_id";
  block_id: string;
} | {
  type: "page_id";
  page_id: string;
} | {
  type: "workspace";
}
用户对象 (User Object)
{
  "object": "user",
  "id": "string"
}
文本块类型
段落 (Paragraph)
类型标识: ​​​​paragraph​​​​
{
  "type": "paragraph",
  "data": {
    "rich_text": "RichText[]",
    "text_color": "Color",
    "background_color": "Color"
  }
}
属性说明:
​​​​rich_text​​​​: 富文本内容数组
​​​​text_color​​​​: 文本颜色
​​​​background_color​​​​: 背景颜色
标题 (Heading)
类型标识: ​​​​heading_1​​​​, ​​​​heading_2​​​​, ​​​​heading_3​​​​
{
  "type": "heading_1",
  "data": {
    "rich_text": "RichText[]",
    "text_color": "Color",
    "background_color": "Color"
  }
}
属性说明:
​​​​rich_text​​​​: 标题文本内容
​​​​text_color​​​​: 文本颜色
​​​​background_color​​​​: 背景颜色
类型区别:
​​​​heading_1​​​​: 一级标题
​​​​heading_2​​​​: 二级标题
​​​​heading_3​​​​: 三级标题
列表项 (List Item)
类型标识: ​​​​bulleted_list_item​​​​, ​​​​numbered_list_item​​​​
{
  "type": "bulleted_list_item",
  "data": {
    "rich_text": "RichText[]",
    "text_color": "Color",
    "background_color": "Color"
  }
}
属性说明:
​​​​rich_text​​​​: 列表项文本内容
​​​​text_color​​​​: 文本颜色
​​​​background_color​​​​: 背景颜色
类型区别:
​​​​bulleted_list_item​​​​: 无序列表项 (圆点)
​​​​numbered_list_item​​​​: 有序列表项 (数字)
待办事项 (To Do)
类型标识: ​​​​to_do​​​​
{
  "type": "to_do",
  "data": {
    "rich_text": "RichText[]",
    "checked": "boolean",
    "text_color": "Color",
    "background_color": "Color"
  }
}
属性说明:
​​​​rich_text​​​​: 待办事项文本内容
​​​​checked​​​​: 是否已完成
​​​​text_color​​​​: 文本颜色
​​​​background_color​​​​: 背景颜色
引用 (Quote)
类型标识: ​​​​quote​​​​
{
  "type": "quote",
  "data": {
    "rich_text": "RichText[]",
    "text_color": "Color",
    "background_color": "Color"
  }
}
属性说明:
​​​​rich_text​​​​: 引用文本内容
​​​​text_color​​​​: 文本颜色
​​​​background_color​​​​: 背景颜色
折叠块 (Toggle)
类型标识: ​​​​toggle​​​​
{
  "type": "toggle",
  "data": {
    "rich_text": "RichText[]",
    "text_color": "Color",
    "background_color": "Color"
  }
}
属性说明:
​​​​rich_text​​​​: 折叠块标题文本
​​​​text_color​​​​: 文本颜色
​​​​background_color​​​​: 背景颜色
媒体块类型
代码块 (Code)
类型标识: ​​​​code​​​​
{
  "type": "code",
  "data": {
    "rich_text": "RichText[]",
    "language": "string"
  }
}
属性说明:
​​​​rich_text​​​​: 代码内容
​​​​language​​​​: 编程语言标识
支持的语言:
​​​​C​​​​, ​​​​C#​​​​, ​​​​C++​​​​, ​​​​Clojure​​​​, ​​​​CMake​​​​, ​​​​Closure Stylesheets (GSS)​​​​, ​​​​CoffeeScript​​​​
​​​​Common Lisp​​​​, ​​​​Crystal​​​​, ​​​​CSS​​​​, ​​​​D​​​​, ​​​​Dart​​​​, ​​​​Django​​​​, ​​​​Dockerfile​​​​, ​​​​diff​​​​
​​​​EBNF​​​​, ​​​​Elm​​​​, ​​​​Erlang​​​​, ​​​​elixir​​​​, ​​​​Fortran​​​​, ​​​​F#​​​​, ​​​​Gherkin​​​​, ​​​​Go​​​​
​​​​Ini​​​​, ​​​​Shell​​​​, ​​​​Groovy​​​​, ​​​​HAML​​​​, ​​​​Haskell​​​​, ​​​​Haxe​​​​, ​​​​HTML​​​​, ​​​​HTTP​​​​
​​​​Java​​​​, ​​​​JavaScript​​​​, ​​​​JSON​​​​, ​​​​Julia​​​​, ​​​​Kotlin​​​​, ​​​​LESS​​​​, ​​​​LiveScript​​​​, ​​​​Lua​​​​
​​​​Markdown​​​​, ​​​​Mathematica​​​​, ​​​​Matlab​​​​, ​​​​MakeFile​​​​, ​​​​Mermaid​​​​, ​​​​Nginx​​​​, ​​​​NSIS​​​​
​​​​Objective-C​​​​, ​​​​Objective-C++​​​​, ​​​​OCaml​​​​, ​​​​Pascal​​​​, ​​​​Perl​​​​, ​​​​PHP​​​​, ​​​​Plain Text​​​​
​​​​PowerShell​​​​, ​​​​Properties files​​​​, ​​​​ProtoBuf​​​​, ​​​​Puppet​​​​, ​​​​Python​​​​, ​​​​Q​​​​, ​​​​R​​​​
​​​​RPM Spec​​​​, ​​​​Ruby​​​​, ​​​​Rust​​​​, ​​​​React​​​​, ​​​​SAS​​​​, ​​​​Scala​​​​, ​​​​Scheme​​​​, ​​​​SCSS​​​​
​​​​Smalltalk​​​​, ​​​​Stylus​​​​, ​​​​SQL​​​​, ​​​​Solidity​​​​, ​​​​Swift​​​​, ​​​​LaTeX​​​​, ​​​​sTeX​​​​, ​​​​Tcl​​​​
​​​​Toml​​​​, ​​​​Twig​​​​, ​​​​TypeScript​​​​, ​​​​VB.NET​​​​, ​​​​VBScript​​​​, ​​​​Verilog​​​​, ​​​​VHDL​​​​
​​​​Vue​​​​, ​​​​XML​​​​, ​​​​XQuery​​​​, ​​​​YAML​​​​
图片 (Image)
类型标识: ​​​​image​​​​
{
  "type": "image",
  "data": {
    "type": "file" | "external",
    "file"?: {
      "url": "string",
      "expiry_time": "string"
    },
    "external"?: {
      "url": "string"
    },
    "caption": "RichText[]"
  }
}
属性说明:
​​​​type​​​​: 图片类型 (​​​​file​​​​ 为内部文件，​​​​external​​​​ 为外部链接)
​​​​file​​​​: 内部文件信息 (包含过期时间)
​​​​external​​​​: 外部链接信息
​​​​caption​​​​: 图片说明文字
文件 (File)
类型标识: ​​​​file​​​​
{
  "type": "file",
  "data": {
    "type": "file" | "external",
    "file"?: {
      "url": "string",
      "expiry_time": "string"
    },
    "external"?: {
      "url": "string"
    },
    "caption": "RichText[]"
  }
}
属性说明:
​​​​type​​​​: 文件类型 (​​​​file​​​​ 为内部文件，​​​​external​​​​ 为外部链接)
​​​​file​​​​: 内部文件信息 (包含过期时间)
​​​​external​​​​: 外部链接信息
​​​​caption​​​​: 文件说明文字
书签 (Bookmark)
类型标识: ​​​​bookmark​​​​
{
  "type": "bookmark",
  "data": {
    "url": "string",
    "caption": "RichText[]"
  }
}
属性说明:
​​​​url​​​​: 书签URL地址
​​​​caption​​​​: 书签说明文字
内嵌 (Embed)
类型标识: ​​​​embed​​​​
{
  "type": "embed",
  "data": {
    "url": "string",
    "caption": "RichText[]"
  }
}
属性说明:
​​​​url​​​​: 内嵌内容URL地址
​​​​caption​​​​: 内嵌内容说明文字
特殊块类型
标注块 (Callout)
类型标识: ​​​​callout​​​​
{
  "type": "callout",
  "data": {
    "rich_text": "RichText[]",
    "icon": "Icon",
    "text_color": "Color",
    "background_color": "Color"
  }
}
属性说明:
​​​​rich_text​​​​: 标注文本内容
​​​​icon​​​​: 图标对象
​​​​text_color​​​​: 文本颜色
​​​​background_color​​​​: 背景颜色
公式 (Equation)
类型标识: ​​​​equation​​​​
{
  "type": "equation",
  "data": {
    "expression": "string"
  }
}
属性说明:
​​​​expression​​​​: LaTeX 数学表达式
页面引用 (Link to Page)
类型标识: ​​​​link_to_page​​​​
{
  "type": "link_to_page",
  "data": {
    "page_id": "string"
  }
}
属性说明:
​​​​page_id​​​​: 被引用页面的ID
模板按钮 (Template)
类型标识: ​​​​template​​​​
{
  "type": "template",
  "data": {
    "rich_text": "RichText[]"
  }
}
属性说明:
​​​​rich_text​​​​: 模板按钮显示文本
同步块 (Synced Block)
类型标识: ​​​​synced_block​​​​
{
  "type": "synced_block",
  "data": {
    "synced_from": {
      "block_id": "string"
    } | null,
    "children": "Block[]"
  }
}
属性说明:
​​​​synced_from​​​​: 同步源块信息 (​​​​null​​​​ 表示原始块)
​​​​children​​​​: 子块列表
布局块类型
分割线 (Divider)
类型标识: ​​​​divider​​​​
{
  "type": "divider",
  "data": {}
}
属性说明:
分割线没有特殊属性
分栏布局 (Column Layout)
类型标识: ​​​​column_list​​​​, ​​​​column​​​​
分栏列表 (Column List)
{
  "type": "column_list",
  "data": {}
}
分栏 (Column)
{
  "type": "column",
  "data": {}
}
属性说明:
分栏布局组件没有特殊属性，通过子块关系形成布局
表格 (Table)
类型标识: ​​​​table​​​​
{
  "type": "table",
  "data": {
    "table_width": "number",
    "has_column_header": "boolean",
    "has_row_header": "boolean"
  }
}
属性说明:
​​​​table_width​​​​: 表格列数
​​​​has_column_header​​​​: 是否有列标题
​​​​has_row_header​​​​: 是否有行标题
表格行 (Table Row)
类型标识: ​​​​table_row​​​​
{
  "type": "table_row",
  "data": {
    "cells": "RichText[][]"
  }
}
属性说明:
​​​​cells​​​​: 单元格内容，二维数组，每个单元格包含富文本数组
子对象块类型
子页面 (Child Page)
类型标识: ​​​​child_page​​​​
{
  "type": "child_page",
  "data": {
    "title": "string"
  }
}
属性说明:
​​​​title​​​​: 子页面标题
子数据库 (Child Database)
类型标识: ​​​​child_database​​​​
{
  "type": "child_database",
  "data": {
    "title": "string"
  }
}
属性说明:
​​​​title​​​​: 子数据库标题
数据类型定义
富文本 (RichText)
富文本是一个对象数组，支持多种类型的内容段落：
type RichText = TextRichText | MentionRichText | EquationRichText;
文本类型 (Text)
{
  "type": "text",
  "text": {
    "content": "string",
    "link": {
      "url": "string"
    } | null
  },
  "annotations": "Annotations",
  "plain_text": "string",
  "href": "string | null"
}
提及类型 (Mention)
{
  "type": "mention",
  "mention": {
    "type": "user" | "page" | "date",
    "user"?: {
      "id": "string"
    },
    "page"?: {
      "id": "string"
    },
    "date"?: {
      "start": "string",
      "end": "string | null",
      "time_zone": "string | null"
    }
  },
  "annotations": "Annotations",
  "plain_text": "string",
  "href": "string | null"
}
公式类型 (Equation)
{
  "type": "equation",
  "data": {
    "expression": "string"
  },
  "annotations": "Annotations",
  "plain_text": "string",
  "href": "string | null"
}
注解 (Annotations)
{
  "bold": "boolean",
  "italic": "boolean",
  "strikethrough": "boolean",
  "underline": "boolean",
  "code": "boolean",
  "color": "Color"
}
属性说明:
​​​​bold​​​​: 粗体
​​​​italic​​​​: 斜体
​​​​strikethrough​​​​: 删除线
​​​​underline​​​​: 下划线
​​​​code​​​​: 代码格式
​​​​color​​​​: 文本颜色
颜色 (Color)
type Color = 
  | "default"
  | "gray" 
  | "brown"
  | "orange"
  | "yellow"
  | "green"
  | "blue"
  | "purple"
  | "pink"
  | "red";
支持的颜色值:
​​​​default​​​​: 默认颜色
​​​​gray​​​​: 灰色
​​​​brown​​​​: 棕色
​​​​orange​​​​: 橙色
​​​​yellow​​​​: 黄色
​​​​green​​​​: 绿色
​​​​blue​​​​: 蓝色
​​​​purple​​​​: 紫色
​​​​pink​​​​: 粉色
​​​​red​​​​: 红色
图标 (Icon)
图标支持多种类型：
Emoji 图标
{
  "emoji": "string"
}
文件图标
{
  "type": "file",
  "data": {
    "url": "string",
    "expiry_time": "string"
  }
}
外部链接图标
{
  "type": "external",
  "external": {
    "url": "string"
  }
}
属性说明:
​​​​emoji​​​​: Unicode emoji 字符
​​​​type​​​​: 图标类型 (​​​​file​​​​ 或 ​​​​external​​​​)
​​​​file.url​​​​: 内部文件URL
​​​​file.expiry_time​​​​: 文件过期时间 (ISO 8601 格式)
​​​​external.url​​​​: 外部图片URL
示例:
// Emoji 图标
{
  "emoji": "💡"
}

// 文件图标
{
  "type": "file",
  "data": {
    "url": "https://cdn2.flowus.cn/files/abc123",
    "expiry_time": "2023-12-01T15:00:00.000Z"
  }
}

// 外部图标
{
  "type": "external",
  "external": {
    "url": "https://example.com/icon.png"
  }
}
日期格式说明
日期字段支持多种格式：
仅日期
{
  "start": "2023-12-01",
  "end": null,
  "time_zone": null
}
日期时间
{
  "start": "2023-12-01T14:30:00",
  "end": null,
  "time_zone": null
}
日期范围
{
  "start": "2023-12-01",
  "end": "2023-12-03",
  "time_zone": null
}
日期时间范围
{
  "start": "2023-12-01T09:00:00",
  "end": "2023-12-01T17:00:00",
  "time_zone": "Asia/Shanghai"
}
完整示例
复杂段落块示例
{
  "object": "block",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "parent": {
    "type": "block_id",
    "block_id": "550e8400-e29b-41d4-a716-446655440001"
  },
  "created_time": "2023-12-01T10:00:00.000Z",
  "created_by": {
    "object": "user",
    "id": "user-550e8400-e29b-41d4-a716-446655440000"
  },
  "last_edited_time": "2023-12-01T10:30:00.000Z",
  "last_edited_by": {
    "object": "user",
    "id": "user-550e8400-e29b-41d4-a716-446655440001"
  },
  "archived": false,
  "has_children": false,
  "type": "paragraph",
  "data": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "这是一个包含",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "这是一个包含",
        "href": null
      },
      {
        "type": "text",
        "text": {
          "content": "粗体文字",
          "link": null
        },
        "annotations": {
          "bold": true,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "red"
        },
        "plain_text": "粗体文字",
        "href": null
      },
      {
        "type": "text",
        "text": {
          "content": "和",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "和",
        "href": null
      },
      {
        "type": "mention",
        "mention": {
          "type": "user",
          "user": {
            "id": "user-550e8400-e29b-41d4-a716-446655440002"
          }
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "@张三",
        "href": null
      },
      {
        "type": "text",
        "text": {
          "content": "的复杂段落。",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "的复杂段落。",
        "href": null
      }
    ],
    "text_color": "default",
    "background_color": "yellow"
  }
}
标注块示例
{
  "object": "block",
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "parent": {
    "type": "page_id",
    "page_id": "550e8400-e29b-41d4-a716-446655440004"
  },
  "created_time": "2023-12-01T11:00:00.000Z",
  "created_by": {
    "object": "user",
    "id": "user-550e8400-e29b-41d4-a716-446655440000"
  },
  "last_edited_time": "2023-12-01T11:00:00.000Z",
  "last_edited_by": {
    "object": "user",
    "id": "user-550e8400-e29b-41d4-a716-446655440000"
  },
  "archived": false,
  "has_children": false,
  "type": "callout",
  "data": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "这是一个重要提示信息！",
          "link": null
        },
        "annotations": {
          "bold": true,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "这是一个重要提示信息！",
        "href": null
      }
    ],
    "icon": {
      "emoji": "⚠️"
    },
    "text_color": "default",
    "background_color": "yellow"
  }
}
表格行示例
{
  "object": "block",
  "id": "550e8400-e29b-41d4-a716-446655440005",
  "parent": {
    "type": "block_id",
    "block_id": "550e8400-e29b-41d4-a716-446655440006"
  },
  "created_time": "2023-12-01T12:00:00.000Z",
  "created_by": {
    "object": "user",
    "id": "user-550e8400-e29b-41d4-a716-446655440000"
  },
  "last_edited_time": "2023-12-01T12:00:00.000Z",
  "last_edited_by": {
    "object": "user",
    "id": "user-550e8400-e29b-41d4-a716-446655440000"
  },
  "archived": false,
  "has_children": false,
  "type": "table_row",
  "data": {
    "cells": [
      [
        {
          "type": "text",
          "text": {
            "content": "产品名称",
            "link": null
          },
          "annotations": {
            "bold": true,
            "italic": false,
            "strikethrough": false,
            "underline": false,
            "code": false,
            "color": "default"
          },
          "plain_text": "产品名称",
          "href": null
        }
      ],
      [
        {
          "type": "text",
          "text": {
            "content": "价格",
            "link": null
          },
          "annotations": {
            "bold": true,
            "italic": false,
            "strikethrough": false,
            "underline": false,
            "code": false,
            "color": "default"
          },
          "plain_text": "价格",
          "href": null
        }
      ],
      [
        {
          "type": "text",
          "text": {
            "content": "状态",
            "link": null
          },
          "annotations": {
            "bold": true,
            "italic": false,
            "strikethrough": false,
            "underline": false,
            "code": false,
            "color": "default"
          },
          "plain_text": "状态",
          "href": null
        }
      ]
    ]
  }
}
块类型兼容性
支持子块的类型
以下块类型可以包含子块 (​​​​has_children: true​​​​)：
​​​​paragraph​​​​ (段落)
​​​​heading_1​​​​, ​​​​heading_2​​​​, ​​​​heading_3​​​​ (标题)
​​​​bulleted_list_item​​​​, ​​​​numbered_list_item​​​​ (列表项)
​​​​to_do​​​​ (待办事项)
​​​​quote​​​​ (引用)
​​​​toggle​​​​ (折叠块)
​​​​callout​​​​ (标注块)
​​​​column_list​​​​ (分栏列表)
​​​​column​​​​ (分栏)
​​​​synced_block​​​​ (同步块)
​​​​child_page​​​​ (子页面)
​​​​child_database​​​​ (子数据库)
​​​​table​​​​ (表格，仅包含 ​​​​table_row​​​​ 子块)
不支持子块的类型
以下块类型不能包含子块 (​​​​has_children: false​​​​)：
​​​​code​​​​ (代码块)
​​​​image​​​​ (图片)
​​​​file​​​​ (文件)
​​​​bookmark​​​​ (书签)
​​​​embed​​​​ (内嵌)
​​​​equation​​​​ (公式)
​​​​link_to_page​​​​ (页面引用)
​​​​template​​​​ (模板按钮)
​​​​divider​​​​ (分割线)
​​​​table_row​​​​ (表格行)
特殊约束
​​​​table​​​​ 块只能包含 ​​​​table_row​​​​ 类型的子块
​​​​column_list​​​​ 块只能包含 ​​​​column​​​​ 类型的子块
​​​​synced_block​​​​ 的内容由同步源决定，不能直接编辑子块
版本兼容性
API 版本：v1
支持的块类型:
​​✅​​ 所有基础文本块 (paragraph, heading, list, to_do, quote, toggle)
​​✅​​ 所有媒体块 (code, image, file, bookmark, embed)
​​✅​​ 所有特殊块 (callout, equation, link_to_page, template, synced_block)
​​✅​​ 所有布局块 (divider, column_list, column, table, table_row)
​​✅​​ 所有子对象块 (child_page, child_database)
颜色支持:
​​✅​​ 块级别颜色 (​​​​text_color​​​​, ​​​​background_color​​​​)
​​✅​​ 富文本级别颜色 (​​​​annotations.color​​​​)
​​✅​​ 完整的颜色值支持
富文本支持:
​​✅​​ 文本格式化 (bold, italic, strikethrough, underline, code)
​​✅​​ 链接支持
​​✅​​ 用户提及 (@用户)
​​✅​​ 页面提及 (页面引用)
​​✅​​ 日期提及 (日期和时间)
​​✅​​ 数学公式
相关文档
Blocks API 文档 - API 接口详细说明
插件开发指南 - 插件开发完整指南
Pages API 文档 - 页面管理 API
Database API 文档 - 数据库管理 API
搜索标题/内容
📔
块 API 文档
概述
Blocks API 提供了类似 Notion 的块管理能力，包括获取、创建、更新和删除各种类型的内容块。支持段落、标题、列表、多媒体、布局等多种块类型，以及完整的颜色和格式化功能。
基础信息
API 版本
Plain Text
1
v1
基础 URL
正式环境
Plain Text
1
https://api.flowus.cn/v1
测试环境
https://api-test.allflow.cn/v1
认证
所有 API 请求都需要在 Authorization 头中包含有效的机器人令牌：
Authorization: Bearer <bot_token>
获取机器人令牌： 请参考 插件开发指南 了解如何创建集成应用和获取机器人访问令牌。
API 接口
1. 获取单个块
获取指定块的详细信息。
请求
GET /v1/blocks/{block_id}
路径参数
​​​​block_id​​​​ (string, 必填): 要获取的块ID
响应示例
{
  "object": "block",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "parent": {
    "type": "block_id",
    "block_id": "550e8400-e29b-41d4-a716-446655440001"
  },
  "created_time": "2023-12-01T10:00:00.000Z",
  "created_by": {
    "object": "user",
    "id": "user-550e8400-e29b-41d4-a716-446655440000"
  },
  "last_edited_time": "2023-12-01T10:30:00.000Z",
  "last_edited_by": {
    "object": "user",
    "id": "user-550e8400-e29b-41d4-a716-446655440001"
  },
  "archived": false,
  "has_children": true,
  "type": "paragraph",
  "data": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "这是一个段落块",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "这是一个段落块",
        "href": null
      }
    ],
    "text_color": "default",
    "background_color": "default"
  }
}
2. 获取块的子块
获取指定块的直接子块列表，支持分页。
请求
GET /v1/blocks/{block_id}/children
路径参数
​​​​block_id​​​​ (string, 必填): 父块ID
查询参数
​​​​page_size​​​​ (integer, 可选): 每页返回的块数量，取值范围 1-100，默认 50
​​​​start_cursor​​​​ (string, 可选): 分页游标，使用子块的ID作为游标值
响应示例
{
  "object": "list",
  "results": [
    {
      "object": "block",
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "type": "paragraph",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "子块内容",
              "link": null
            }
          }
        ],
        "text_color": "default",
        "background_color": "default"
      }
    }
  ],
  "next_cursor": "550e8400-e29b-41d4-a716-446655440002",
  "has_more": true,
  "type": "block",
  "block": {}
}
3. 追加子块
向指定块追加一个或多个子块。
请求
PATCH /v1/blocks/{block_id}/children
路径参数
​​​​block_id​​​​ (string, 必填): 父块ID
请求体
{
  "children": [
    {
      "type": "paragraph",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "新段落内容",
              "link": null
            },
            "annotations": {
              "bold": false,
              "italic": false,
              "strikethrough": false,
              "underline": false,
              "code": false,
              "color": "default"
            }
          }
        ],
        "text_color": "blue",
        "background_color": "yellow"
      }
    }
  ]
}
限制
单次最多创建 100 个子块
每个子块必须指定有效的类型
响应示例
{
  "object": "list",
  "results": [
    {
      "object": "block",
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "type": "paragraph",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "新段落内容",
              "link": null
            }
          }
        ],
        "text_color": "blue",
        "background_color": "yellow"
      }
    }
  ],
  "next_cursor": null,
  "has_more": false,
  "type": "block",
  "block": {}
}
4. 更新块
更新现有块的内容、类型或属性。
请求
PATCH /v1/blocks/{block_id}
路径参数
​​​​block_id​​​​ (string, 必填): 要更新的块ID
4.1 更新块内容
请求体示例
{
  "data": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "更新后的段落内容",
          "link": null
        },
        "annotations": {
          "bold": true,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "red"
        }
      }
    ],
    "text_color": "red",
    "background_color": "yellow"
  }
}
4.2 更改块类型
请求体示例
{
  "type": "heading_1",
  "data": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "现在是一级标题",
          "link": null
        },
        "annotations": {
          "bold": true,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        }
      }
    ],
    "text_color": "blue",
    "background_color": "default"
  }
}
4.3 归档块
请求体示例
{
  "archived": true
}
响应示例
{
  "object": "block",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "heading_1",
  "data": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "现在是一级标题",
          "link": null
        }
      }
    ],
    "text_color": "blue",
    "background_color": "default"
  }
}
5. 删除块
删除指定块及其所有子块。此操作不可逆。
请求
DELETE /v1/blocks/{block_id}
路径参数
​​​​block_id​​​​ (string, 必填): 要删除的块ID
响应示例
{
  "object": "block",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "deleted": true
}
支持的块类型
FlowUs Blocks API 支持丰富的块类型，涵盖文本、媒体、布局等各种内容形式：
块类型概览
类别
块类型
说明
颜色支持
所有文本类块类型都支持双层颜色系统：
块级别颜色：​​​​text_color​​​​ 和 ​​​​background_color​​​​
富文本级别颜色：​​​​annotations.color​​​​
支持的颜色值：​​​​default​​​​, ​​​​gray​​​​, ​​​​brown​​​​, ​​​​orange​​​​, ​​​​yellow​​​​, ​​​​green​​​​, ​​​​blue​​​​, ​​​​purple​​​​, ​​​​pink​​​​, ​​​​red​​​​
详细说明： 每种块类型的具体对象结构、属性定义和使用示例，请参考 Block 对象实体文档。
富文本对象
富文本对象用于表示格式化的文本内容，支持以下类型：
支持的富文本类型
类型
描述
用途
格式化支持
所有富文本类型都支持 ​​​​annotations​​​​ 格式化：
样式：​​​​bold​​​​, ​​​​italic​​​​, ​​​​strikethrough​​​​, ​​​​underline​​​​, ​​​​code​​​​
颜色：​​​​color​​​​ (支持所有标准颜色值)
链接：​​​​href​​​​ 和 ​​​​text.link​​​​
详细说明： 富文本对象的完整结构定义和使用示例，请参考 Block 对象实体文档。
使用示例
创建复杂内容结构
PATCH /v1/blocks/parent-block-id/children
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "children": [
    {
      "type": "heading_1",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "项目文档",
              "link": null
            },
            "annotations": {
              "bold": true,
              "color": "blue"
            }
          }
        ],
        "text_color": "blue",
        "background_color": "default"
      }
    },
    {
      "type": "callout",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "这是一个重要提示，请仔细阅读！",
              "link": null
            }
          }
        ],
        "icon": {
          "emoji": "⚠️"
        },
        "text_color": "default",
        "background_color": "yellow"
      }
    },
    {
      "type": "paragraph",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "项目负责人：",
              "link": null
            }
          },
          {
            "type": "mention",
            "mention": {
              "type": "user",
              "user": {
                "id": "user-123"
              }
            }
          },
          {
            "type": "text",
            "text": {
              "content": "，完成时间：",
              "link": null
            }
          },
          {
            "type": "mention",
            "mention": {
              "type": "date",
              "date": {
                "start": "2023-12-31",
                "end": null,
                "time_zone": null
              }
            }
          }
        ],
        "text_color": "default",
        "background_color": "default"
      }
    },
    {
      "type": "to_do",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "完成需求分析",
              "link": null
            }
          }
        ],
        "checked": true,
        "text_color": "green",
        "background_color": "default"
      }
    },
    {
      "type": "to_do",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "完成代码开发",
              "link": null
            }
          }
        ],
        "checked": false,
        "text_color": "default",
        "background_color": "default"
      }
    },
    {
      "type": "code",
      "data": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "function calculateProgress() {\n  const completed = tasks.filter(t => t.done).length;\n  const total = tasks.length;\n  return (completed / total) * 100;\n}",
              "link": null
            }
          }
        ],
        "language": "javascript"
      }
    },
    {
      "type": "divider",
      "data": {}
    },
    {
      "type": "table",
      "data": {
        "table_width": 3,
        "has_column_header": true,
        "has_row_header": false
      }
    }
  ]
}
更新块内容和颜色
PATCH /v1/blocks/block-id
Authorization: Bearer your_bot_token
Content-Type: application/json

{
  "data": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "这是更新后的内容，",
          "link": null
        },
        "annotations": {
          "bold": true,
          "color": "red"
        }
      },
      {
        "type": "text",
        "text": {
          "content": "部分文字有特殊格式。",
          "link": null
        },
        "annotations": {
          "italic": true,
          "underline": true,
          "color": "blue"
        }
      }
    ],
    "text_color": "default",
    "background_color": "yellow"
  }
}
错误处理
HTTP 状态码
状态码
描述
错误响应格式
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "请求参数验证失败",
  "details": {
    "field": "children",
    "reason": "必须提供至少一个子块"
  }
}
常见错误类型
1. 参数验证错误 (validation_error)
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "必须提供至少一个子块"
}
2. 权限不足 (forbidden)
{
  "object": "error",
  "status": 403,
  "code": "forbidden",
  "message": "机器人没有访问此块的权限"
}
3. 块不存在 (not_found)
{
  "object": "error",
  "status": 404,
  "code": "not_found",
  "message": "指定的块不存在"
}
4. 块类型不支持 (unsupported_block_type)
{
  "object": "error",
  "status": 422,
  "code": "unsupported_block_type",
  "message": "不支持的块类型: invalid_type"
}
API 限制
请求限制
单次创建块数量：最多100个子块
富文本长度：单个富文本段落最大2000字符
嵌套深度：块嵌套深度不超过50层
分页大小：分页查询最大页面大小为100
频率限制
读取操作：每分钟1000次请求
写入操作：每分钟100次请求
批量操作：每分钟10次请求
存储限制
文件大小：单个文件最大100MB
图片尺寸：最大20MB，推荐尺寸不超过4K
总存储：根据空间套餐限制
最佳实践
1. 操作优化
批量操作：一次性创建多个块而不是逐个创建
分页处理：对于大量子块，使用分页获取
合理使用：避免不必要的API调用
2. 错误处理
重试机制：对于临时错误实现合理重试
优雅降级：当某些块类型不支持时提供备选方案
用户反馈：向用户提供清晰的错误信息
3. 内容结构
层次清晰：合理使用标题层级组织内容
格式一致：保持相同类型内容的格式一致性
颜色适度：避免过度使用颜色造成视觉干扰
4. 权限管理
最小权限：机器人只申请必要的权限
权限检查：在操作前检查机器人权限
错误处理：处理权限不足的情况
相关文档
Block 对象实体文档 - 所有块类型的详细对象结构和属性定义
插件开发指南 - 了解如何创建集成应用和获取机器人Token
机器人API详细文档 - 机器人API的完整参考
Pages API文档 - 页面管理API
Database API文档 - 数据库管理API
快速参考
常用块类型创建模板
段落
{
  "type": "paragraph",
  "data": {
    "rich_text": [{"type": "text", "text": {"content": "内容"}}],
    "text_color": "default",
    "background_color": "default"
  }
}
标题
{
  "type": "heading_1",
  "data": {
    "rich_text": [{"type": "text", "text": {"content": "标题"}}],
    "text_color": "default",
    "background_color": "default"
  }
}
代办事项
{
  "type": "to_do",
  "data": {
    "rich_text": [{"type": "text", "text": {"content": "任务"}}],
    "checked": false,
    "text_color": "default",
    "background_color": "default"
  }
}
代码块
{
  "type": "code",
  "data": {
    "rich_text": [{"type": "text", "text": {"content": "代码"}}],
    "language": "javascript"
  }
}
标注块
{
  "type": "callout",
  "data": {
    "rich_text": [{"type": "text", "text": {"content": "提示"}}],
    "icon": {"emoji": "💡"},
    "text_color": "default",
    "background_color": "yellow"
  }
}
搜索标题/内容
📖
User API 文档
概述
机器人用户 API 提供了获取机器人创建者信息的功能。这些API允许机器人了解创建它的用户信息。
认证
所有 API 请求都需要在 HTTP 头中包含机器人的 Bearer Token：
Plain Text
1
Authorization: Bearer your_bot_token_here
API 接口
获取机器人创建者信息
获取当前机器人的创建者用户信息。
请求
HTTP
1
GET /v1/users/me
权限要求
机器人需要具备 ​​​​readContent​​​​ 能力
响应
成功响应 (200 OK):
{
  "object": "user",
  "id": "875bb809-eab6-467f-80d9-a7de6899d885",
  "type": "person",
  "person": {
    "email": "user@example.com"
  },
  "name": "张三",
  "avatar_url": "https://cdn2.flowus.cn/avatar123.jpg"
}
响应字段说明
字段
类型
描述
是否必须
​​​​object​​​​
​​​​string​​​​
对象类型，总是 ​​​​"user"​​​​
是
​​​​id​​​​
​​​​string​​​​
用户的唯一标识符 (UUID)
是
​​​​type​​​​
​​​​string​​​​
用户类型，总是 ​​​​"person"​​​​
是
错误响应
401 Unauthorized - 认证失败:
{
  "error": {
    "code": "unauthorized",
    "message": "缺少Authorization header"
  }
}
403 Forbidden - 权限不足:
{
  "error": {
    "code": "forbidden", 
    "message": "机器人没有readContent权限"
  }
}
404 Not Found - 创建者不存在:
{
  "error": {
    "code": "not_found",
    "message": "机器人创建者不存在"
  }
}
使用示例
JavaScript 示例
class FlowUsBot {
  constructor(token) {
    this.token = token;
    this.baseUrl = 'https://api.flowus.cn';
  }

  async getMe() {
    const response = await fetch(`${this.baseUrl}/v1/users/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
  }
}

// 使用示例
async function example() {
  const bot = new FlowUsBot('your_bot_token_here');
  
  try {
    const creator = await bot.getMe();
    console.log('机器人创建者信息:', {
      id: creator.id,
      name: creator.name,
      email: creator.person?.email,
      hasAvatar: !!creator.avatar_url
    });
  } catch (error) {
    console.error('获取创建者信息失败:', error.message);
  }
}
cURL 示例
curl -X GET "https://api.flowus.cn/v1/users/me" \
  -H "Authorization: Bearer your_bot_token_here" \
  -H "Content-Type: application/json"
Python 示例
import requests

class FlowUsBot:
    def __init__(self, token):
        self.token = token
        self.base_url = 'https://api.flowus.cn'
    
    def get_me(self):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f'{self.base_url}/v1/users/me', headers=headers)
        response.raise_for_status()
        return response.json()

# 使用示例
if __name__ == '__main__':
    bot = FlowUsBot('your_bot_token_here')
    
    try:
        creator = bot.get_me()
        print(f"创建者: {creator['name']} ({creator['id']})")
        if creator.get('person', {}).get('email'):
            print(f"邮箱: {creator['person']['email']}")
    except requests.RequestException as e:
        print(f"请求失败: {e}")
使用场景
1. 个性化欢迎消息
根据机器人创建者的信息，生成个性化的欢迎消息：
async function generateWelcomeMessage(bot) {
  const creator = await bot.getMe();
  const name = creator.name || '用户';
  return `Hello ${name}! 我是您创建的FlowUs机器人，很高兴为您服务！`;
}
搜索标题/内容
搜索 API 文档
概述
搜索 API 允许机器人在其授权的页面范围内进行智能搜索。该接口支持全文搜索和语义搜索，返回相关的页面结果。
接口详情
搜索页面
在机器人授权的页面范围内搜索相关内容。
请求方式： ​​​​POST /v1/search​​​​
请求头：
Plain Text
1
Authorization: Bearer your_bot_token_here
2
Content-Type: application/json
请求参数：
参数
类型
必填
描述
默认值
​​​​query​​​​
​​​​string​​​​
否
搜索关键词
​​​​""​​​​
​​​​start_cursor​​​​
​​​​string​​​​
否
分页游标，用于获取下一页结果
-
​​​​page_size​​​​
​​​​number​​​​
否
每页返回的结果数量，范围 1-100
​​​​10​​​​
请求示例：
JSON
1
{
2
  "query": "项目计划",
3
  "start_cursor": "eyJvZmZzZXQiOjEwfQ==",
4
  "page_size": 20
5
}
响应格式：
{
  "object": "list",
  "results": [
    {
      "object": "page",
      "id": "a1b2c3d4-5678-9012-3456-789012345678",
      "created_time": "2024-01-01T10:00:00.000Z",
      "last_edited_time": "2024-01-15T14:30:00.000Z",
      "parent": {
        "type": "database_id",
        "database_id": "d9824bdc-8445-4327-be8b-5b47500af6ce"
      },
      "archived": false,
      "properties": {
        "title": {
          "type": "title",
          "title": [
            {
              "type": "text",
              "text": {
                "content": "项目计划文档"
              }
            }
          ]
        }
      }
    }
  ],
  "next_cursor": "eyJvZmZzZXQiOjIwfQ==",
  "has_more": true
}
响应对象说明
搜索结果对象
属性
类型
描述
页面结果对象
属性
类型
描述
父级对象类型
页面的父级对象可以是以下几种类型之一：
1. 空间父级
{
  "type": "space_id",
  "space_id": "workspace-uuid"
}
2. 数据库父级
{
  "type": "database_id",
  "database_id": "database-uuid"
}
3. 页面父级
{
  "type": "page_id",
  "page_id": "page-uuid"
}
4. 块父级
{
  "type": "block_id",
  "block_id": "block-uuid"
}
搜索行为
搜索范围
搜索仅限于机器人已授权访问的页面
包括页面标题和页面内容
支持模糊匹配和语义搜索
搜索结果排序
默认按相关性排序
相关性相同时按最后编辑时间降序排列
分页机制
使用 Base64 编码的 JSON 游标进行分页
游标包含偏移量信息：​​​​{"offset": 20}​​​​
最大页面大小为 100 项
使用示例
基础搜索
curl -X POST https://api.flowus.cn/v1/search \
  -H "Authorization: Bearer your_bot_token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "会议记录",
    "page_size": 10
  }'
分页搜索
# 获取第一页
curl -X POST https://api.flowus.cn/v1/search \
  -H "Authorization: Bearer your_bot_token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "项目",
    "page_size": 20
  }'

# 获取下一页（使用返回的 next_cursor）
curl -X POST https://api.flowus.cn/v1/search \
  -H "Authorization: Bearer your_bot_token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "项目",
    "start_cursor": "eyJvZmZzZXQiOjIwfQ==",
    "page_size": 20
  }'
空查询搜索
# 返回所有授权页面
curl -X POST https://api.flowus.cn/v1/search \
  -H "Authorization: Bearer your_bot_token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "page_size": 50
  }'
错误处理
常见错误代码
状态码
错误代码
描述
错误响应示例
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "page_size 必须在 1 到 100 之间"
}
权限要求
机器人必须具有 ​​​​readContent​​​​ 权限
只能搜索机器人已授权访问的页面
搜索结果会自动过滤掉无权限访问的页面
