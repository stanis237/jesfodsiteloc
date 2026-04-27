if settings.DEBUG:
    urlparttens += static(settings.static_url, document_root= settings.staticfiles_dir[0])
    urlpattens += static(settings.media_url, document_root =settings.media_root)