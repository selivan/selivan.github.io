---
layout: post
title:  "Smooth deploy of a loaded PHP web application with php-fpm and nginx, without downtime or errors"
tags: [php,nginx,deploy]
comments_by_utterance: true
---

**UPDATE 2020-05-10** Added the cachetool option, thanks to reddit users [ds11](https://www.reddit.com/u/ds11) and [SevereHeight](https://www.reddit.com/u/SevereHeight) for mentioning it.

Generally, the smoothest way to deploy a loaded web app without downtime or erros is by adding instances(hosts, containers) with the new version to balancer and then removing old ones, when they have served all running requests. But sometimes it is easier to switch app versions on instances without re-configuring balancer.

Here is how to do that with php-fpm and nginx.

After deploying the application(with [deployer](https://deployer.org) or whatever tool you prefer) you have directories with old and new application versions, shared files(like logs), and symlink `current` pointing to the new version. Like this:

```
/var/www/example.com:

releases/
    2020-04-08-12-00-00/
    2020-04-08-15-00-00/
shared/
    logs/
current -> releases/2020-04-08-15-00-00
```

Using the `current` symlink directly in nginx config may cause some troubles.

php-fpm is not designed to have app files suddenly change/disappear. Some of requests in progress when switching symlink may return 500 errors.

I suggest instead to use the absolute path to the required app version in nginx configs:

`/etc/nginx/sites-enabled/example.com:`

```
include /var/www/example.com/root_dir.nginx.conf;
root $root_dir;
```

`/var/www/example.com/root_dir.nginx.conf:`

```
set $root_dir /var/www/example.com/2020-04-08-15-00-00/public;
```

File `root_dir.nginx.conf` is updated on deploy, then nginx is reloaded. Nginx reload is done very carefully, all requests in progress are completed by old workers with the old config version, pointing to the old application version. Users won't experience any errors or slowdown.

Now the only thing left to do is to clear the old code from php opcache. You can do that with [opcache_reset()](https://www.php.net/manual/en/function.opcache-reset.php) function. This function should be called from a PHP process using the fpm pool you want to reset the opcache for.

First option is to create a php file and make it accessible from localhost:

`/var/www/localhost/opcache_reset.php:`

```
<?php
header('Content-Type:text/plain');
try {
    if (opcache_reset()){
        print "SUCCESS: opcache_reset\n";
    } else {
        throw new Exception("ERROR: opcache is disabled\n", 500);
    }
} catch ( Exception $e) {
    http_response_code($e->getCode()?:500);
    print $e->getMessage();
}
```

`/etc/nginx/sites-enabled/localhost:`

```
server {
    listen 127.0.0.1:80;
    location / { return 403; }
    location = /opcache_reset {
        include fastcgi_params.conf;
        fastcgi_split_path_info ^(.+\.php)(/.*)$;
        fastcgi_pass  unix:/var/run/php/phpXX-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root/opcache_reset.php;
    }
```

Second option is using [cachetool](https://gordalina.github.io/cachetool/). It can connect directly to php-fpm unix socket or tcp port, no need to serve special php files. There is a ready [deployer recipie](https://deployer.org/recipes/cachetool.html) to use it.

Finally, here is [deployer](https://deployer.org) config to do all that, example extending the symfony4 recipie with separate php file:

`deploy-example-com.php:`

```
namespace Deployer;
require 'recipe/symfony4.php';

desc('generate nginx config and reload');
task('nginx:update_config_and_reload', function () {
    run('echo "set \$root_dir {{release_path}}/public;" > {{deploy_path}}/root_dir.nginx.conf');
    run('sudo --non-interactive nginx -t'); // avoid reloading with incorrect config
    run('sudo --non-interactive systemctl reload nginx.service');
});

desc('call php-fpm opcache_reset from localhost');
task('php-fpm:localhost:opcache_reset', function () {
    run('curl http://localhost/opcache_reset');
});

after('deploy:symlink', 'nginx:update_config_and_reload');
after('nginx:update_config_and_reload', 'php-fpm:localhost:opcache_reset');

inventory('inventory.yml');
set('deploy_path','/var/www/example.com/');
set('repository', 'git@gitlab.local:my/example-com.git');
... // some other perameters
```

And example with cachetool:

`deploy-example-com.php:`

```
namespace Deployer;
require 'recipe/symfony4.php';
require 'recipe/cachetool.php';

desc('generate nginx config and reload');
task('nginx:update_config_and_reload', function () {
    run('echo "set \$root_dir {{release_path}}/public;" > {{deploy_path}}/root_dir.nginx.conf');
    run('sudo --non-interactive nginx -t'); // avoid reloading with incorrect config
    run('sudo --non-interactive systemctl reload nginx.service');
});

after('deploy:symlink', 'nginx:update_config_and_reload');
after('nginx:update_config_and_reload', 'cachetool:clear:opcache');

inventory('inventory.yml');
set('deploy_path','/var/www/example.com/');
set('repository', 'git@gitlab.local:my/example-com.git');
set('cachetool', '/var/run/php/phpXX-fpm.sock');
... // some other perameters
```

Note that deploy user should have rights to reload nginx service with sudo and to check nginx config(run `nginx -t`).
