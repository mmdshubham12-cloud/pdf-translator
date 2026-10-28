# راهنمای فایل‌های KV

## فایل‌های KV

### 1. main_screen.kv

صفحه اصلی برای انتخاب فایل PDF و شروع ترجمه

**عناصر اصلی:**
- دکمه آپلود فایل
- دکمه شروع ترجمه
- انتخاب خروجی (HTML/PDF)
- نمایش آمار

**کلاس‌های استفاده شده:**
- `MDTopAppBar`: نوار ابزار
- `MDScrollView`: اسکرول‌ور
- `MDCard`: کارت‌ها
- `MDLabel`: برچسب‌ها
- `MDRaisedButton`: دکمه‌ها
- `MDCheckbox`: چک‌باکس‌ها
- `MDProgressBar`: نوار پیشرفت
- `MDFloatingActionButton`: دکمه شناور

### 2. settings_screen.kv

صفحه تنظیمات برای مدیریت کلیدهای API و پروفایل‌ها

**عناصر اصلی:**
- لیست کلیدهای API
- افزودن کلید جدید
- تنظیم کلید پیش‌فرض
- تغییر پروفایل
- تنظیمات اضافی

**کلاس‌های استفاده شده:**
- `MDTextField`: فیلد متنی
- `MDList`: لیست
- `OneLineListItem`: آیتم لیست
- `MDCheckbox`: چک‌باکس‌ها

### 3. progress_screen.kv

صفحه نمایش پیشرفت ترجمه

**عناصر اصلی:**
- نوار پیشرفت
- آمار ترجمه
- لاگ ترجمه
- دکمه‌های کنترل

**کلاس‌های استفاده شده:**
- `MDLabel`: برچسب‌ها
- `MDProgressBar`: نوار پیشرفت
- `MDScrollView`: اسکرول‌ور
- `MDList`: لیست

## ساختار فایل KV

### هدر KV

```yaml
#:kivy 1.11.1
```

این خط نسخه Kivy را مشخص می‌کند.

### کلاس‌ها

```yaml
<ScreenName>:
    orientation: 'vertical'
    # تنظیمات کلاس

    MDTopAppBar:
        title: "Screen Title"
        # تنظیمات نوار ابزار

    MDScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            padding: 'dp(20)'
            spacing: 'dp(20)'

            MDLabel:
                text: "Label Text"
                # تنظیمات برچسب
```

### تنظیمات رایج

#### Padding

```yaml
padding: 'dp(20)'
```

برای فاصله داخلی.

#### Spacing

```yaml
spacing: 'dp(20)'
```

برای فاصله بین عناصر.

#### Size Hint

```yaml
size_hint_y: None
height: 'dp(50)'
```

برای تنظیم ارتفاع ثابت.

#### Position Hint

```yaml
pos_hint: {'center_x': 0.5, 'center_y': 0.5}
```

برای موقعیت‌دهی.

#### Colors

```yaml
md_bg_color: app.theme_cls.primary_color
text_color: app.theme_cls.primary_color
```

برای رنگ‌ها.

## استایل‌ها

### فونت

```yaml
font_style: 'H6'
font_style: 'Body1'
font_style: 'Caption'
```

### رنگ‌ها

```yaml
text_color: app.theme_cls.primary_color
text_color: app.theme_cls.accent_color
```

### سایه

```yaml
elevation: 6
```

### گردی

```yaml
radius: [15, 15, 0, 0]
```

## انیمیشن‌ها

```yaml
MDRaisedButton:
    # تنظیمات دکمه
    on_release: app.on_button_press()
```

## تعاملات

```yaml
MDRaisedButton:
    text: "Button"
    on_release: app.on_button_press()
```

## دکمه‌ها

### MDRaisedButton

```yaml
MDRaisedButton:
    text: "Button"
    icon: "plus"
    on_release: app.on_button_press()
```

### MDFloatingActionButton

```yaml
MDFloatingActionButton:
    icon: "plus"
    on_release: app.on_button_press()
```

### MDIconButton

```yaml
MDIconButton:
    icon: "plus"
    on_release: app.on_button_press()
```

## فیلدها

### MDTextField

```yaml
MDTextField:
    hint_text: "Hint Text"
    mode: "rectangle"
    multiline: False
```

### MDTextArea

```yaml
MDTextArea:
    hint_text: "Hint Text"
    mode: "rectangle"
```

## لیست‌ها

### MDList

```yaml
MDList:
    OneLineListItem:
        text: "Item 1"
        on_release: app.on_item_press()
```

### MDRecycleView

```yaml
MDRecycleView:
    RecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
```

## اسکرول‌ورها

### MDScrollView

```yaml
MDScrollView:
    MDBoxLayout:
        orientation: 'vertical'
```

### MDListScrollView

```yaml
MDListScrollView:
    MDList:
        OneLineListItem:
            text: "Item"
```

## نوار ابزار

### MDTopAppBar

```yaml
MDTopAppBar:
    title: "Title"
    elevation: 4
    left_action_items: [['menu', lambda x: app.on_menu_click()]]
    right_action_items: [['search', lambda x: app.on_search_click()]]
```

## کارت‌ها

### MDCard

```yaml
MDCard:
    orientation: 'vertical'
    padding: 'dp(20)'
    radius: [15]
```

## چک‌باکس‌ها

### MDCheckbox

```yaml
MDCheckbox:
    text: "Checkbox"
    active: True
    on_active: app.on_checkbox_active(self.active)
```

## نوار پیشرفت

### MDProgressBar

```yaml
MDProgressBar:
    value: 50
    size_hint_y: None
    height: 'dp(10)'
```

## نمونه کامل

```yaml
#:kivy 1.11.1

<MainScreen>:
    orientation: 'vertical'

    MDTopAppBar:
        title: "متریک PDF"
        elevation: 4
        background_color: app.theme_cls.primary_color

    MDScrollView:

        MDBoxLayout:
            orientation: 'vertical'
            padding: 'dp(20)'
            spacing: 'dp(20)'

            MDCard:
                orientation: 'vertical'
                padding: 'dp(20)'
                radius: [15]

                MDLabel:
                    text: "انتخاب فایل PDF"
                    halign: 'center'
                    font_style: 'H6'

                MDFloatingActionButton:
                    icon: 'upload'
                    on_release: app.on_upload_click()

            MDRaisedButton:
                text: "شروع ترجمه"
                on_release: app.on_translate_click()

            MDCheckbox:
                text: "HTML"
                on_active: app.on_html_checkbox(self.active)

            MDCheckbox:
                text: "PDF"
                on_active: app.on_pdf_checkbox(self.active)
```

## نکات مهم

1. **نسخه Kivy**: همیشه نسخه Kivy را مشخص کنید
2. **Padding و Spacing**: از مقادیر dp استفاده کنید
3. **Colors**: از theme_cls استفاده کنید
4. **Interaction**: همیشه on_release را اضافه کنید
5. **Layout**: از layout مناسب استفاده کنید

## بهینه‌سازی

### استفاده از MDScrollView

- برای لیست‌های طولانی
- برای اسکرول‌ورها
- برای بهینه‌سازی مصرف حافظه

### استفاده از RecycleView

- برای لیست‌های بسیار طولانی
- برای بهینه‌سازی مصرف حافظه

### استفاده از کلاس‌های محدود

- از کلاس‌های کمتر استفاده کنید
- از کلاس‌های پیشرفته استفاده کنید
- برای بهینه‌سازی مصرف حافظه
