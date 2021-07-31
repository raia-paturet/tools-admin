SET varaiable .env

FIRST LAUNCH:

pip3 install -r requirement.txt
sh script_init.sh

RUN 
python3 runner.py runserver


creation admin:
INSERT INTO users (email) VALUES ('admin@gmail.com');

INSERT INTO roles (name) VALUES ('admin');

INSERT INTO user_roles (user_id, role_id) VALUES (15, 2);
INSERT 0 1
