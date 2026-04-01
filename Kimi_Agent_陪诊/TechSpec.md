# 陪诊小程序技术规范

---

## 1. 组件清单

### shadcn/ui 组件
| 组件 | 用途 |
|------|------|
| Button | 各种按钮 |
| Card | 卡片容器 |
| Input | 表单输入框 |
| Label | 表单标签 |
| Select | 下拉选择 |
| RadioGroup | 单选服务类型 |
| Textarea | 多行文本输入 |
| ScrollArea | 横向滚动区域 |
| Avatar | 用户头像 |
| Badge | 标签徽章 |
| Tabs | 页面切换 |
| Carousel | 轮播图 |

### 自定义组件
| 组件 | 用途 |
|------|------|
| BottomNav | 底部导航栏 |
| HospitalCard | 医院卡片 |
| EscortCard | 陪诊师卡片 |
| ServiceTypeCard | 服务类型选择卡片 |
| TimeSelector | 时间选择器 |

---

## 2. 动画实现方案

| 动画 | 库 | 实现方式 | 复杂度 |
|------|------|----------|--------|
| 页面过渡 | Framer Motion | AnimatePresence + 滑动动画 | 中 |
| 轮播图 | Embla Carousel | shadcn Carousel 组件 | 低 |
| 元素入场 | Framer Motion | whileInView + stagger | 中 |
| 按钮悬停 | CSS/Tailwind | hover:scale + transition | 低 |
| 触摸反馈 | Framer Motion | whileTap scale | 低 |
| 卡片滚动 | CSS | overflow-x-auto + snap | 低 |

---

## 3. 项目结构

```
src/
├── components/
│   ├── ui/              # shadcn/ui 组件
│   ├── BottomNav.tsx    # 底部导航
│   ├── HospitalCard.tsx # 医院卡片
│   ├── EscortCard.tsx   # 陪诊师卡片
│   └── ServiceCard.tsx  # 服务类型卡片
├── pages/
│   ├── Home.tsx         # 首页
│   ├── Training.tsx     # 培训报名
│   └── Booking.tsx      # 预约陪诊
├── hooks/
│   └── useScrollAnimation.ts
├── lib/
│   └── utils.ts
├── App.tsx
└── main.tsx
```

---

## 4. 依赖列表

```json
{
  "dependencies": {
    "framer-motion": "^11.x",
    "embla-carousel-react": "^8.x",
    "lucide-react": "^0.x"
  }
}
```

---

## 5. 路由设计

| 路径 | 页面 | 说明 |
|------|------|------|
| / | Home | 首页 |
| /training | Training | 培训报名 |
| /booking | Booking | 预约陪诊 |

---

## 6. 响应式断点

- 移动端: < 768px (主要适配)
- 小程序场景，以 375px 为基准设计
