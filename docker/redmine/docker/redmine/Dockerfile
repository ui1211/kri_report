ARG REDMINE_IMAGE_TAG=6.1
FROM redmine:${REDMINE_IMAGE_TAG}

ARG REDMINE_ISSUES_TREE_REF=6.1.x
ARG REDMICA_UI_EXTENSION_REF=master

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends git; \
    git clone --depth 1 --branch "${REDMINE_ISSUES_TREE_REF}" https://github.com/Loriowar/redmine_issues_tree.git /usr/src/redmine/plugins/redmine_issues_tree; \
    git clone --depth 1 --branch "${REDMICA_UI_EXTENSION_REF}" https://github.com/redmica/redmica_ui_extension.git /usr/src/redmine/plugins/redmica_ui_extension; \
    apt-get purge -y --auto-remove git; \
    rm -rf /var/lib/apt/lists/*; \
    bundle config set without 'development test'; \
    bundle install; \
    mkdir -p /home/redmine/.bundle; \
    chown -R redmine:redmine /home/redmine /usr/src/redmine/plugins
