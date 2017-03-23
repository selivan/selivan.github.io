
location / {

    error_page 404 @err404;
}

location @err404 {
    ssi on;
    root /var/www/ssi;
    try_files err404.shtml =404;
}
