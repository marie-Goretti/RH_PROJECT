from django.core.management.base import BaseCommand
import random
from personnel.models import Employe, Departement

class Command(BaseCommand):
    help = 'Réassigne les employés de Ressources Humaines vers Logistique et autres'

    def handle(self, *args, **kwargs):
        try:
            rh_dept = Departement.objects.filter(nom__icontains='Ressources Humaines').first()
            if not rh_dept:
                raise Departement.DoesNotExist
        except Departement.DoesNotExist:
            self.stdout.write(self.style.ERROR("Le département Ressources Humaines n'existe pas."))
            return

        rh_employes = list(Employe.objects.filter(departement=rh_dept))
        
        if len(rh_employes) <= 2:
            self.stdout.write(self.style.WARNING(f"Il n'y a que {len(rh_employes)} employé(s) en RH. Aucune modification nécessaire."))
            return

        # On en garde exactement 2 au hasard
        employes_to_keep = random.sample(rh_employes, 2)
        employes_to_move = [emp for emp in rh_employes if emp not in employes_to_keep]

        other_depts = list(Departement.objects.exclude(id=rh_dept.id))
        
        if not other_depts:
            self.stdout.write(self.style.ERROR("Il n'y a pas d'autres départements pour transférer les employés."))
            return

        logistique_dept = next((d for d in other_depts if 'Logistique' in d.nom), None)

        moved_count = 0
        for emp in employes_to_move:
            # 50% de chance d'aller en logistique (comme demandé explicitement), 50% ailleurs
            if logistique_dept and random.random() < 0.5:
                emp.departement = logistique_dept
            else:
                emp.departement = random.choice(other_depts)
            emp.save()
            moved_count += 1

        self.stdout.write(self.style.SUCCESS(f"{moved_count} employés ont été retirés des RH. Il n'en reste que 2 dans ce département."))
