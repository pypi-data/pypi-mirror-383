# Django Yandex Ad Manager

A comprehensive Django application for managing and displaying Yandex advertising blocks with advanced configuration options.
See the comprehensive guide on https://timthewebmaster.com/en/tools/django-yandex-ad-manager/

## Features

- **Multiple Ad Types**: Support for banners, full-screen ads, floor ads, top ads, carousels, and in-image ads
- **Platform Targeting**: Display ads on specific platforms (desktop, mobile, or cross-platform)
- **Flexible Configuration**: Manage ad locations, display frequency, and placement rules
- **Middleware Integration**: Automatic ad injection into templates based on view and template rules
- **Customizable Templates**: Extensible template system for different ad formats
- **Context-Aware**: Smart ad placement with context data integration
- **Pagination Support**: Automatic ad insertion between content pages

## Installation

```bash
pip install django-yandex-ad-manager
```

## Requirements

- Django 3.2+
- Python 3.7+

## Configuration

### 1. Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ...
    'django_yandex_ad_manager.apps.YandexadmanagerConfig',
    # ...
]
```

### 2. Add Middleware

```python
MIDDLEWARE = [
    # ...
    'django_yandex_ad_manager.middleware.AdManagerMiddleware',
    # ...
]
```

### 4. Set up allowed views and templates, to render into
```python
# Yandex ad manager
# For example, you should paste your view's names and templates
YANDEX_AD_MANAGER__ALLOWED_VIEWS = ('home', 'article', 'tool', 'tool_main')
YANDEX_AD_MANAGER__ALLOWED_TEMPLATES = ('PagiScroll/base_post_list.html', 'Post/basic--post_preview-article.html', 'Post/basic--post_preview-note.html', 'Post/basic--post_preview-tool.html' )
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Configure Static Files

Make sure to collect static files after installation:

```bash
python manage.py collectstatic
```

## Models Overview

### YandexAdBlock
Defines individual ad blocks with properties:
- **Ad Types**: `banner`, `fullscreen`, `floorAd`, `topAd`, `feed`, `inImage`
- **Push Triggers**: `on-load`, `on-intersection`
This means when your website should make a request to Yandex, to retrieve an Ad. 
    - **on-load** means as soon as possible
    - **on-intersection** means when users viewport intersects with an Ad element.
- **Platform Targeting**: `desktop`, `mobile`, `crossplatform`

### YandexAdLocation
Maps ad blocks to specific locations on your site. You should specify them by yourself

### YandexAdBlockConfiguration
Groups ad locations and defines display frequency.

### YandexCurrentAdBlockConfiguration
Singleton model to manage the currently active ad configuration.

## Template Integration Examples

### 1. Required Headers in Base Template

Include these in your base template's head section (`<head>` tag):

```django
{% if isYandexAdManagerMiddlewareConnected %}
    {% include 'YandexAdManager/admanager_header.html' %}
{% endif %}
```

### 2. Styles and Scripts

Include in your base template's styles and scripts blocks:

```django
{% block styles %}
    {% if isYandexAdManagerMiddlewareConnected %}
        {% include 'YandexAdManager/admanager_styles.html' %}
    {% endif %}
{% endblock %}

{% block scripts %}
    {% if isYandexAdManagerMiddlewareConnected %}
        {% include 'YandexAdManager/admanager_scripts.html' %}
    {% endif %}
{% endblock %}
```

## Ad Placement Examples
The blocks below should be used whenever you want your ad to be displayed. This is not applied to those Ad blocks without containers (topAd, floorAd, fullscreen, inImage) 

### Single element Integration

```django
{% if isYandexAdManagerMiddlewareConnected %}
    {% for adlocation in adlocations %}
        {% if adlocation.adlocation_name == "HOME_FIRST_VISIBLE" %}
            {% include 'YandexAdManager/admanager_element.html' with adblock=adlocation.adblock%}
        {% endif %}
    {% endfor %}
{% endif %}
```

### Multiple elements Integration
**unificator** should be used only if you use one YandexAdBlock for different location on the same page

```django
{% if isYandexAdManagerMiddlewareConnected %}
    {% for adlocation in adlocations %}
        {% if adlocation.adlocation_name == "HOME_FIRST_VISIBLE" %}
            {% include 'YandexAdManager/admanager_element.html' with adblock=adlocation.adblock unificator="home_first_visible" %}
        {% endif %}
        {% if adlocation.adlocation_name == "HOME_SECOND_VISIBLE" %}
            {% include 'YandexAdManager/admanager_element.html' with adblock=adlocation.adblock unificator="home_second_visible" %}
        {% endif %}
    {% endfor %}
{% endif %}


```
### Paginated Lists Integration

```django
{% if isYandexAdManagerMiddlewareConnected %}
    {# Ads between articles in pagination #}
    {% for adlocation in adlocations %}
        {% if adlocation.adlocation_name == "ON_PAGISCROLL_ARTICLES_BETWEEN_PAGES" %}
            {% include 'YandexAdManager/admanager_element_in_pagination.html' with page=page adblock=adlocation.adblock %}
        {% endif %}
    {% endfor %}
{% endif %}
```

## Advanced Configuration

### Display Frequency Control

Control how often ads appear in paginated lists:

```python
# In YandexAdBlockConfiguration model
adnetwork_step_by = 3  # Show ad every 3 items
```

### Platform Targeting

```python
# Available options
PlatformToDisplay.CROSSPLATFORM  # All devices
PlatformToDisplay.DESKTOP        # Desktop only  
PlatformToDisplay.MOBILE         # Mobile only
```

### Push Triggers

```python
PushOn.ON_LOAD           # Load immediately
PushOn.ON_INTERSECTION   # Load when visible in viewport
```

## Middleware Configuration

The `AdManagerMiddleware` automatically injects context data and handles ad placement:

```python
class AdManagerMiddleware:
    allowed_views = ('home', 'article', 'tool', 'tool_main')
    allowed_templates = (
        'PagiScroll/base_post_list.html',
        'Post/basic--post_preview-article.html',
        'Post/basic--post_preview-note.html', 
        'Post/basic--post_preview-tool.html'
    )
```

## Best Practices

1. **Use descriptive unificators** to track ad performance in different locations
2. **Test on multiple devices** when using platform targeting
3. **Monitor ad density** to avoid overwhelming users
4. **Use intersection-based loading** for better performance
5. **Configure appropriate ad types** for different content contexts

## Troubleshooting

### Ads Not Showing
- Check if middleware is properly configured
- Verify `isYandexAdManagerMiddlewareConnected` is True in templates
- Ensure ad locations are properly configured in admin
- Check browser console for JavaScript errors

### Performance Issues
- Use `ON_INTERSECTION` for non-critical ads
- Minimize use of full-screen ads
- Implement lazy loading where appropriate

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

ISC License - see package.json for details.

## Support

For issues and questions, please open an issue on the GitHub repository.

## Compatibility

- Django 3.2, 4.0, 4.1, 4.2
- Python 3.7, 3.8, 3.9, 3.10, 3.11

---

**Note**: This package is not officially affiliated with Yandex. It's a community-maintained Django integration for Yandex Advertising Network.