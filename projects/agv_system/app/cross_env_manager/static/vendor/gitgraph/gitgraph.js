/**
 * 简化的Git图形库 - 用于AGV配置系统备份历史可视化
 * 这是一个简化版本，提供基本的Git图形功能
 */

(function (global, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        global.GitGraph = factory();
    }
}(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    // 默认配置
    const defaultConfig = {
        element: null,
        template: 'metro',
        orientation: 'vertical',
        mode: 'compact',
        author: 'AGV Config System',
        initCommitOffsetX: 50,
        initCommitOffsetY: 50,
        commitMessage: {
            display: true,
            displayAuthor: true,  // 显示作者信息
            displayHash: true,    // 显示哈希信息
            displayBranch: true
        }
    };

    // 颜色模板
    const templates = {
        metro: {
            colors: ['#0366d6', '#28a745', '#6f42c1', '#e36209', '#6a737d', '#005cc5'],
            branch: {
                lineWidth: 3,
                spacingX: 80,
                spacingY: 100  // 大幅增加垂直间距以容纳多行文本
            },
            commit: {
                spacingX: 80,
                spacingY: 80,  // 增加提交点之间的垂直间距
                dot: {
                    size: 12,  // 稍微增大点的大小
                    strokeWidth: 2
                },
                message: {
                    display: true,
                    displayAuthor: false,
                    displayHash: false,
                    font: '12px Arial, sans-serif',
                    maxWidth: 200,  // 添加最大宽度限制
                    lineHeight: 16   // 行高
                }
            }
        }
    };

    // Git图形类
    class GitGraph {
        constructor(config) {
            this.config = { ...defaultConfig, ...config };
            this.element = typeof this.config.element === 'string' 
                ? document.querySelector(this.config.element) 
                : this.config.element;
            
            if (!this.element) {
                throw new Error('GitGraph: element is required');
            }

            this.template = templates[this.config.template] || templates.metro;
            this.branches = {};
            this.currentBranch = null;
            this.commits = [];
            this.commitCounter = 0;
            
            this._init();
        }

        _init() {
            // 清空容器
            this.element.innerHTML = '';
            
            // 创建SVG容器
            this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            this.svg.setAttribute('width', '100%');
            this.svg.setAttribute('height', '100%');
            this.svg.setAttribute('class', 'gitgraph-svg');
            this.element.appendChild(this.svg);
            
            // 创建分组用于提交
            this.commitsGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            this.commitsGroup.setAttribute('class', 'gitgraph-commits');
            this.svg.appendChild(this.commitsGroup);
            
            // 创建分组用于分支线
            this.branchesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            this.branchesGroup.setAttribute('class', 'gitgraph-branches');
            this.svg.appendChild(this.branchesGroup);
        }
        
        // 更新SVG高度以容纳所有提交
        _updateSvgHeight() {
            if (this.commits.length === 0) return;
            
            // 计算所需的总高度
            const lastCommit = this.commits[this.commits.length - 1];
            const template = this.template;
            const config = this.config;
            
            // 计算总高度：最后一个提交的Y坐标 + 额外空间
            let totalHeight = lastCommit.y + 150; // 额外150px空间
            
            // 确保SVG高度足够显示所有提交
            // 获取容器元素的实际高度
            const containerHeight = this.element.clientHeight;
            
            // 总是设置SVG高度为计算的总高度，确保所有内容都可见
            this.svg.setAttribute('height', totalHeight + 'px');
            
            // 如果容器有滚动条，确保SVG宽度也适应
            const containerWidth = this.element.clientWidth;
            this.svg.setAttribute('width', '100%');
        }

        // 创建分支
        branch(name) {
            const branch = new Branch(this, name);
            this.branches[name] = branch;
            
            if (!this.currentBranch) {
                this.currentBranch = branch;
            }
            
            return branch;
        }

        // 添加提交
        _addCommit(options) {
            const commit = new Commit(this, options);
            this.commits.push(commit);
            this.commitCounter++;
            
            // 渲染提交
            commit.render();
            
            // 更新SVG高度以容纳所有提交
            this._updateSvgHeight();
            
            return commit;
        }
    }

    // 分支类
    class Branch {
        constructor(gitgraph, name) {
            this.gitgraph = gitgraph;
            this.name = name;
            this.commits = [];
            this.color = this._getBranchColor();
        }

        _getBranchColor() {
            const colors = this.gitgraph.template.colors;
            const branchNames = Object.keys(this.gitgraph.branches);
            const index = branchNames.length % colors.length;
            return colors[index];
        }

        // 在分支上提交
        commit(options) {
            const commitOptions = {
                ...options,
                branch: this,
                color: this.color
            };
            
            const commit = this.gitgraph._addCommit(commitOptions);
            this.commits.push(commit);
            
            // 绘制分支线
            if (this.commits.length > 1) {
                this._drawBranchLine(this.commits[this.commits.length - 2], commit);
            }
            
            return commit;
        }

        _drawBranchLine(fromCommit, toCommit) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', fromCommit.x);
            line.setAttribute('y1', fromCommit.y);
            line.setAttribute('x2', toCommit.x);
            line.setAttribute('y2', toCommit.y);
            line.setAttribute('stroke', this.color);
            line.setAttribute('stroke-width', this.gitgraph.template.branch.lineWidth);
            line.setAttribute('class', 'gitgraph-branch-line');
            
            this.gitgraph.branchesGroup.appendChild(line);
        }
    }

    // 提交类
    class Commit {
        constructor(gitgraph, options) {
            this.gitgraph = gitgraph;
            this.options = options;
            this.branch = options.branch;
            this.color = options.color || '#0366d6';
            this.x = 0;
            this.y = 0;
            this.element = null;
            
            // 计算位置
            this._calculatePosition();
        }

        _calculatePosition() {
            const config = this.gitgraph.config;
            const template = this.gitgraph.template;
            
            // 简单的位置计算 - 使用gitgraph的commitCounter来确保唯一位置
            const commitIndex = this.gitgraph.commitCounter;
            
            if (config.orientation === 'horizontal') {
                this.x = config.initCommitOffsetX + (commitIndex * template.commit.spacingX);
                this.y = config.initCommitOffsetY;
            } else {
                this.x = config.initCommitOffsetX;
                this.y = config.initCommitOffsetY + (commitIndex * template.commit.spacingY);
            }
        }

        render() {
            // 创建提交组
            const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            group.setAttribute('class', 'gitgraph-commit');
            group.setAttribute('transform', `translate(${this.x}, ${this.y})`);
            
            // 创建提交点
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', 0);
            circle.setAttribute('cy', 0);
            circle.setAttribute('r', this.gitgraph.template.commit.dot.size);
            circle.setAttribute('fill', this.color);
            circle.setAttribute('stroke', this.color);
            circle.setAttribute('stroke-width', this.gitgraph.template.commit.dot.strokeWidth);
            circle.setAttribute('class', 'gitgraph-commit-dot');
            
            // 添加点击事件
            if (this.options.onClick) {
                circle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.options.onClick.call(this, e);
                });
            }
            
            // 添加鼠标悬停事件
            if (this.options.onMouseOver) {
                circle.addEventListener('mouseover', (e) => {
                    this.options.onMouseOver.call(this, e);
                });
            }
            
            // 添加鼠标离开事件
            if (this.options.onMouseOut) {
                circle.addEventListener('mouseout', (e) => {
                    this.options.onMouseOut.call(this, e);
                });
            }
            
            group.appendChild(circle);
            
            // 创建提交消息
            if (this.gitgraph.config.commitMessage.display && this.options.subject) {
                const config = this.gitgraph.config.commitMessage;
                let messageText = this.options.subject;
                
                // 添加作者信息
                if (config.displayAuthor && this.options.author) {
                    messageText += `\n作者: ${this.options.author}`;
                }
                
                // 添加哈希信息
                if (config.displayHash && this.options.hash) {
                    messageText += `\n版本: ${this.options.hash}`;
                }
                
                // 添加时间戳信息
                if (this.options.timestamp) {
                    const date = new Date(this.options.timestamp);
                    const timeStr = date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'});
                    messageText += `\n时间: ${timeStr}`;
                }
                
                // 创建多行文本
                const lines = messageText.split('\n');
                const lineHeight = this.gitgraph.template.commit.message.lineHeight;
                const startY = 20; // 从提交点下方20px开始
                
                lines.forEach((line, index) => {
                    // 截断过长的文本
                    let displayLine = line;
                    const maxChars = 25; // 每行最大字符数
                    if (displayLine.length > maxChars) {
                        displayLine = displayLine.substring(0, maxChars - 3) + '...';
                    }
                    
                    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    text.setAttribute('x', 25); // 从提交点右侧25px开始
                    text.setAttribute('y', startY + (index * lineHeight));
                    text.setAttribute('class', 'gitgraph-commit-message');
                    text.setAttribute('fill', 'var(--text-color)');
                    text.setAttribute('font-family', 'Arial, sans-serif');
                    text.setAttribute('font-size', index === 0 ? '13px' : '11px'); // 第一行大一点
                    text.setAttribute('font-weight', index === 0 ? 'bold' : 'normal'); // 第一行加粗
                    text.textContent = displayLine;
                    
                    // 添加标题样式
                    if (index === 0) {
                        text.setAttribute('class', 'gitgraph-commit-title');
                    }
                    
                    group.appendChild(text);
                });
                
                // 添加背景矩形（可选，用于更好的可读性）
                if (lines.length > 1) {
                    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                    const rectWidth = 220;
                    const rectHeight = startY + (lines.length * lineHeight) - 5;
                    rect.setAttribute('x', 15);
                    rect.setAttribute('y', 5);
                    rect.setAttribute('width', rectWidth);
                    rect.setAttribute('height', rectHeight);
                    rect.setAttribute('fill', 'var(--bg-color)');
                    rect.setAttribute('fill-opacity', '0.8');
                    rect.setAttribute('stroke', 'var(--border-color)');
                    rect.setAttribute('stroke-width', '1');
                    rect.setAttribute('rx', '4');
                    rect.setAttribute('ry', '4');
                    rect.setAttribute('class', 'gitgraph-commit-background');
                    
                    // 将背景插入到第一个元素之前
                    group.insertBefore(rect, circle.nextSibling);
                }
            }
            
            this.element = group;
            this.gitgraph.commitsGroup.appendChild(group);
        }
    }

    // 导出GitGraph
    return GitGraph;
}));