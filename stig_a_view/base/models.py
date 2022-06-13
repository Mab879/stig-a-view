from django.db import models
from django.utils.translation import gettext_lazy as _

SEVERITY = {'high': 0, 'medium': 1, 'low': 2}


class Product(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.short_name


class Stig(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    release = models.PositiveIntegerField()
    version = models.PositiveIntegerField()
    release_date = models.DateField()

    @property
    def short_version(self):
        return f'V{self.version}R{self.release}'

    def __str__(self) -> str:
        return f'<Stig {self.product} v{self.version}r{self.release}>'


class Srg(models.Model):
    srg_id = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.srg_id


class Cci(models.Model):
    cci_id = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.cci_id


class Control(models.Model):
    stig = models.ForeignKey(Stig, on_delete=models.CASCADE)
    srg = models.ForeignKey(Srg, on_delete=models.CASCADE)
    vulnerability_id = models.PositiveIntegerField()
    disa_stig_id = models.CharField(max_length=50)

    class Severity(models.IntegerChoices):
        HIGH = '0', _('high')
        MEDIUM = '1', _('medium')
        LOW = '2', _('low')

    severity = models.IntegerField(choices=Severity.choices, default=Severity.HIGH)
    title = models.TextField()
    description = models.TextField()
    cci = models.ForeignKey(Cci, on_delete=models.CASCADE)
    fix_text = models.TextField()
    fix = models.TextField()
    check_content = models.TextField()

    def __str__(self) -> str:
        return self.disa_stig_id
