import os
import random
import string
from sqlalchemy.exc import IntegrityError
from natsort import os_sorted

from scutwork.components import db
from scutwork.models import User, Paragraph


def add_admin():
    admin = User(username = 'Ilya_MZP',
            name='Илья Ковченков',
            active = True)
    admin.set_role('Admin')
    admin.set_password('1q2w3e4r5t6y')
    db.session.add(admin)
    db.session.commit()

def populate_data():
    letters = string.ascii_lowercase
    for root, dirs, files in os.walk(os.path.join(os.getcwd(),"data")):
        for file in os_sorted(files):
            if file.endswith('.html'):
                header = file.partition("_")[2][:-5]
                with open(os.path.join(root, file), 'r') as f:
                    body = f.read()
                    link = ''.join(random.choice(letters) for i in range(10))
                    paragraph = Paragraph(link=link, header=header,body=body)
                    db.session.add(paragraph)
                    db.session.commit()
                    f.close()
