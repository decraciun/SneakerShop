import schedule
import time, os, django
from datetime import datetime, timedelta
from django.utils.timezone import now
from aplicatie.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
import sys
sys.path.append(r'C:\Users\Denis\Desktop\Proiect+Django')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proiect.settings')
django.setup()

def sterge_utilizatori_neconfirmati():
    limita = now() - timedelta(minutes=2)
    utilizatori_stersi = CustomUser.objects.filter(email_confirmat=False, date_joined__lt=limita).delete()
    print(f"{utilizatori_stersi[0]} utilizatori șterși la {datetime.now()}.")

def trimite_newsletter():
    limita = now() - timedelta(minutes=60) 
    utilizatori = CustomUser.objects.filter(date_joined__lt=limita)
    for user in utilizatori:
        print(f"Newsletter trimis catre {user.email} la {datetime.now()}.")

def trimite_email_test():
    send_mail(
        subject='Test Email',
        message='Acesta este un email de test trimis la fiecare 10 minute.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin[1] for admin in settings.ADMINS],
    )
    print("Email trimis catre admin la fiecare 10 minute.")

def trimite_email_testtest():
    send_mail(
        subject='Test Test Email',
        message='Acesta este un email de test trimis miercuri la ora 15:00.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin[1] for admin in settings.ADMINS],
    )
    print("Email trimis către admin miercuri la ora 15:00.")

schedule.every(2).minutes.do(sterge_utilizatori_neconfirmati)
schedule.every().monday.at("08:00").do(trimite_newsletter)

schedule.every(10).minutes.do(trimite_email_test)
schedule.every().wednesday.at("15:00").do(trimite_email_testtest)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)  # Verifică task-urile o dată pe secundă
