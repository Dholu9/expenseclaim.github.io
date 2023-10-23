from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class ParentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    ClaimNumber = models.IntegerField()
    DateofCreation = models.DateField(auto_now_add=True)
    DeduceEmailAddress = models.EmailField(max_length=30, null=True)
    DTNumber = models.TextField()
    Department = models.CharField(max_length=120)
    Manager = models.CharField(max_length=120)
    ExpenseDetails = models.CharField(max_length=120)


    

class ChildModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    parent = models.ForeignKey(ParentModel, on_delete=models.CASCADE, related_name='child_models',null=True)
    ReceiptNumber = models.CharField(max_length=100)
    ReceiptDate = models.DateField()
    BillAttachment = models.FileField(upload_to='media/', max_length=254,default='default.pdf')
    ExpenseHead = models.CharField(max_length=120)
    ClaimAmount = models.PositiveIntegerField()
    TotalClaimAmount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    Remarks = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)



class ClaimStatus(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    claim = models.ForeignKey(ParentModel, on_delete=models.CASCADE,related_name='claimstatus_set',null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    comments = models.TextField(blank=True, null=True)
    accountscomments = models.TextField(blank=True, null=True)
    accountstatus = models.CharField(max_length=20)
    paymentstatus = models.CharField(max_length=20,default='')
   

    
    

    def __str__(self):
        return f"{self.claim.ClaimNumber} - {self.status}"
    

     
        
        


