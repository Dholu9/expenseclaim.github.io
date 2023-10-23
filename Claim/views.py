from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import ParentModel,ChildModel,ClaimStatus
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.db.models import Max
from datetime import datetime,timedelta
from datetime import date, timedelta
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Sum
from django.core.files.storage import default_storage
from django.conf import settings
import os


 
def index(request):
    if request.method == "POST":
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        user = authenticate(request, last_name=last_name, password=password)         

       
        if user is not None:
            login(request, user)

            if user.groups.filter(name='Manager').exists():  
                return redirect('teams')
            elif user.groups.filter(name='Accounts').exists(): 
                return redirect('claims')
            else:
                return redirect('entereddata')
        else:
            messages.error(request, 'Error Logging In. Please Try Again.')
            return redirect('index')
    else:
        return render(request, "index.html")
    

def logout_user(request):
    logout(request) 
     
    return redirect('index') 

def newclaim(request):
    user=request.user
    first_name = user.first_name
    last_name = user.last_name

    full_name = f"{first_name}" 
    email = user.email
    
    return render(request, "userclaims.html",{'full_name': full_name, 'email': email,'last_name':last_name}) 

def addclaim(request):
    
    return render(request, "userclaims.html")  

def claims(request):
    users = User.objects.all()
    user_count_list = []

    for user in users:
        approved_counts = ParentModel.objects.filter(user=user, claimstatus_set__accountstatus='Accepted').count()
        submitted_counts = ParentModel.objects.filter(user=user,claimstatus_set__status='Approved').exclude(claimstatus_set__accountstatus='Accepted').count()
        paymentdue_counts = ParentModel.objects.filter(user=user, claimstatus_set__accountstatus='Accepted').filter(user=user, claimstatus_set__paymentstatus='').count()

        user_count_list.append({'username': user.username, 'approved_count': approved_counts, 'submitted_count': submitted_counts,'paymentdue_counts': paymentdue_counts})
        
    user_count_list.sort(key=lambda x: x['submitted_count'], reverse=True)

    data = {
        'user_count_list': user_count_list,
    }

    return render(request, "claims.html", data)


def teams(request):
    users = User.objects.all()
    user_count_list = []

    for user in users:
        approved_counts = ParentModel.objects.filter(user=user, claimstatus_set__status='Approved').count()
        submitted_counts = ParentModel.objects.filter(user=user).exclude(claimstatus_set__status='Approved').count()
        accountsrejected = ParentModel.objects.filter(user=user,claimstatus_set__accountstatus='Rejected').count()
     

        user_count_list.append({'username': user.username, 'approved_count': approved_counts, 'submitted_count': submitted_counts, 'accountsrejectedcount':accountsrejected})


    user_count_list.sort(key=lambda x: x['submitted_count'], reverse=True)

    data = {
        'user_count_list': user_count_list,
    }

    return render(request, "teams.html", data)



def associate(request):
    return render(request, "associate.html")  

def demo(request, username):
    user = get_object_or_404(User, username=username)
    parentclaimdata = ParentModel.objects.filter(user=user).order_by('-ClaimNumber')

    user_count_list = []

    user_count_list.append({'username': user.username, 'parentclaimdata': parentclaimdata})


    data = {
        'user_count_list': user_count_list,
        'parentclaimdata':parentclaimdata,
    }

    return render(request, "info.html", data)



def demo2(request, ClaimNumber):
    user=request.user
    parentclaimdata = ParentModel.objects.filter(user=user,ClaimNumber=ClaimNumber).order_by('-ClaimNumber')

    data = {
        'user': user,
        'parentclaimdata': parentclaimdata
    }
    return render(request, "info.html", data)


@login_required
def entereddata(request):
    user = request.user
    last_name = user.last_name
    email = user.email
    parentclaimdata = ParentModel.objects.filter(user=user).order_by('-ClaimNumber')

 
    data = {
        'user': user,
        'parentclaimdata': parentclaimdata,
        'last_name':last_name,
        'email':email,        
    }

    return render(request, "dataentered.html", data)


@login_required
def entereddata2(request, ClaimNumber):

    parentclaimdata = ParentModel.objects.get(ClaimNumber=ClaimNumber) 

    user = parentclaimdata.user 
    first_name = user.first_name
    last_name = user.last_name

    childclaimdata = ChildModel.objects.filter(parent=parentclaimdata)
    
    total_claim_amount = childclaimdata.first().TotalClaimAmount    
    accountscomments = parentclaimdata.claimstatus_set.values_list('accountscomments', flat=True).first()

   
    data = {
        
        'parentclaimdata': parentclaimdata,
        'childclaimdata': childclaimdata,
        'total_claim_amount':total_claim_amount,
        'accountscomments':accountscomments,
        'first_name':first_name,
        'last_name':last_name,


    }
    return render(request, "dataentered2.html", data)

@login_required
def entereddata3(request, ClaimNumber):
   
    parentclaimdata = ParentModel.objects.get(ClaimNumber=ClaimNumber)
    childclaimdata = ChildModel.objects.filter(parent=parentclaimdata)
    total_claim_amount = childclaimdata.first().TotalClaimAmount 
    user = parentclaimdata.user 
    first_name = user.first_name
    last_name = user.last_name

   
    data = {
        
        'parentclaimdata': parentclaimdata,
        'childclaimdata': childclaimdata,
        'total_claim_amount':total_claim_amount,
        'first_name':first_name,
        'last_name':last_name,
    }
    return render(request, "accountsshow.html", data)


def saverecord(request):
    if ParentModel.objects.count() == 0:
        ClaimNumber = 100
    else:
        max_claim = ParentModel.objects.aggregate(max_claim=Max('ClaimNumber'))
        ClaimNumber = int(max_claim['max_claim'] or 0) + 1



    if request.method == "POST":
        DateofCreation = request.POST.get('DateofCreation')
        user = request.user        
        Department = request.POST.get('Department')
        Manager = request.POST.get('Manager')
        ExpenseDetails = request.POST.get('ExpenseDetails')

        en1 = ParentModel(         
            user=user,
            ClaimNumber=ClaimNumber,
            DateofCreation=DateofCreation,            
            Department=Department,
            Manager=Manager,
            ExpenseDetails=ExpenseDetails
        )
        en1.save()

        parent_id = en1.id
        ReceiptNumbers = request.POST.getlist('ReceiptNumber')       
        ReceiptDates = request.POST.getlist('ReceiptDate')     
        ExpenseHeads = request.POST.getlist('ExpenseHead')   
        BillAttachments = request.FILES.getlist('BillAttachment')   
 
        TotalClaimAmount_str = request.POST.get('TotalClaimAmount')
        if TotalClaimAmount_str:
            TotalClaimAmount = int(float(TotalClaimAmount_str))
        else:
            TotalClaimAmount = None

        if BillAttachments:
            BillAttachments.insert(0, '') 
        

        ClaimAmounts = request.POST.getlist('ClaimAmounts')      
        Remarks = request.POST.getlist('Remarks')
      

   
        file_names = []  

        for i in range(len(ReceiptNumbers)):
            ReceiptNumber = ReceiptNumbers[i]
            ReceiptDate = ReceiptDates[i]
            ExpenseHead = ExpenseHeads[i]
            ClaimAmount = ClaimAmounts[i]
            Remark = Remarks[i]
            bill_attachment = BillAttachments[i] if i < len(BillAttachments) else None

     
            if bill_attachment:
                file_name = default_storage.save(bill_attachment.name, bill_attachment)
            else:
                file_name = None  

           
            file_names.append(file_name)

            if ReceiptDate:              
                ReceiptDate = datetime.strptime(ReceiptDate, '%Y-%m-%d').date()
            else:
                ReceiptDate = datetime.now().date()

            if ClaimAmount:
                try:
                    ClaimAmount = int(ClaimAmount)
                except ValueError:
                    ClaimAmount = 1500
            else:
                ClaimAmount = 1500

            en2 = ChildModel(
                parent_id=parent_id,
                ReceiptNumber=ReceiptNumber,
                ReceiptDate=ReceiptDate,
                BillAttachment=file_name,
                ExpenseHead=ExpenseHead,
                ClaimAmount=ClaimAmount,
                TotalClaimAmount=TotalClaimAmount,
                Remarks=Remark
            )

            en2.save()
        return redirect('entereddata')
        
            

    context = {
        'ClaimNumber': ClaimNumber,
        'ClaimAmounts': ClaimAmounts,
        'Remarks': Remarks,
        'file_names': file_names,
    }

    messages.success(request, "Claim submitted successfully!")       
    return render(request, "dataentered.html", context)



def updaterecord(request, ClaimNumber):
    claim = get_object_or_404(ParentModel, ClaimNumber=ClaimNumber)
  
    if request.method == "POST":
        # DateofCreation = datetime.strptime(request.POST.get('DateofCreation'), '%B %d, %Y').date()

        raw_date = request.POST.get('DateofCreation')      
        raw_date = raw_date.replace('Oct.', 'October')

        try:
            DateofCreation = datetime.strptime(raw_date, '%B %d, %Y').date()
        except ValueError:
            # Handle parsing errors as needed
            DateofCreation = None 

        Department = request.POST.get('Department')     
        Manager = request.POST.get('Manager')      
        ExpenseDetails = request.POST.get('ExpenseDetails')
       

        claim.DateofCreation = DateofCreation   
        claim.ExpenseDetails = ExpenseDetails
        claim.Department = Department
        claim.Manager = Manager
        claim.save()

        ReceiptNumbers = request.POST.getlist('ReceiptNumber') 
        print(ReceiptNumbers)    
        ReceiptDates = request.POST.getlist('ReceiptDate')
        print(ReceiptDates) 
        ExpenseHeads = request.POST.getlist('ExpenseHead') 
        print(ExpenseHeads)   
        BillAttachments = request.FILES.getlist('BillAttachment')
        print(BillAttachments)  
        ClaimAmounts = request.POST.getlist('ClaimAmount')
        print(ClaimAmounts)       
        Remarks = request.POST.getlist('Remarks') 
        print(Remarks)
        TotalClaimAmount = request.POST.get('TotalClaimAmount')
        childclaims = ChildModel.objects.filter(parent=claim)  

        

        for i, childclaim in enumerate(childclaims):
            if i < len(ReceiptNumbers):
                ReceiptNumber = ReceiptNumbers[i]
                ReceiptDate = ReceiptDates[i] 
                ExpenseHead = ExpenseHeads[i]
                ClaimAmount = ClaimAmounts[i]
                Remark = Remarks[i]


            
                if i < len(BillAttachments):
                    bill_attachment = BillAttachments[i]
                    if bill_attachment:               
                        file_name = default_storage.save(bill_attachment.name, bill_attachment)
                        childclaim.BillAttachment = file_name


                if ReceiptDate:
                    ReceiptDate = datetime.strptime(ReceiptDate, '%Y-%m-%d').date()
                else:
                    ReceiptDate = datetime.now().date()


                print(ReceiptNumber)
                print(ReceiptDate)
                print(ExpenseHead)
                print(ClaimAmount)
                print(Remark)
              
   
                childclaim.ReceiptNumber=ReceiptNumber
                childclaim.ReceiptDate=ReceiptDate        
                childclaim.ExpenseHead=ExpenseHead
                childclaim.ClaimAmount=ClaimAmount
                childclaim.Remarks=Remark
                childclaim.TotalClaimAmount=TotalClaimAmount
                
                childclaim.save()

 
        
                

        claim_status, created = ClaimStatus.objects.get_or_create(claim=claim)
        claim_status.status = "ReSubmitted"        
        claim_status.save()
        return redirect('entereddata')


    context = {
        'ClaimNumber': ClaimNumber,
        'ClaimAmounts': ClaimAmounts,
        'Remarks': Remarks,
    }
    
    messages.success(request, "Claim submitted successfully!")
    return render(request, "dataentered.html", context)




def showclaim(request, ClaimNumber):
    user = request.user
    first_name = user.first_name
    last_name = user.last_name
    parentclaimdata = get_object_or_404(ParentModel, user=user, ClaimNumber=ClaimNumber)
    childclaimdata = ChildModel.objects.filter(parent=parentclaimdata)



    if childclaimdata.exists():
        total_claim_amount = childclaimdata.first().TotalClaimAmount
    else:
        total_claim_amount = None
   
    is_rejected = parentclaimdata.claimstatus_set.filter(status='Rejected').exists()
    bill_attachments = [child.BillAttachment.name for child in childclaimdata]
    print(bill_attachments)
  
    comments = parentclaimdata.claimstatus_set.values_list('comments', flat=True).first()
    
    data = {
        'user': user,
        'ClaimNumber': ClaimNumber,       
        'parentclaimdata': parentclaimdata,
        'childclaimdata': childclaimdata,
        'is_rejected': is_rejected,
        'bill_attachments': bill_attachments,
        'total_claim_amount': total_claim_amount,
        'comments': comments,
        'first_name':first_name,
        'last_name':last_name,
    }
    
    return render(request, "savedform.html", data)



def review_claim(request, ClaimNumber):
    claim = get_object_or_404(ParentModel, ClaimNumber=ClaimNumber)
    parentclaimdata = ParentModel.objects.get(ClaimNumber=ClaimNumber)
    childclaimdata = ChildModel.objects.filter(parent=parentclaimdata)


    if request.method == 'POST':
        new_status = request.POST.get('status')
        comments = request.POST.get('comments')

        claim_status, created = ClaimStatus.objects.get_or_create(claim=claim)
        claim_status.status = new_status
        claim_status.comments = comments  
        claim_status.save()

        user = claim.user  
        username = user.username 
        return HttpResponseRedirect(reverse('demo', args=(username,)))

    context = {
        'parentclaimdata': parentclaimdata,
     
    }

    return render(request, "teams.html", context)



def accountsview(request,username):

    user = get_object_or_404(User, username=username)
    user_count_list = []
    approvedclaims = ParentModel.objects.filter(user=user, claimstatus_set__status='Approved')
    print(approvedclaims)
    parentclaimdata = ParentModel.objects.filter(user=user,claimstatus_set__status='Approved')
    

    user_count_list.append({'username': user.username, 'approvedclaims': approvedclaims})
    print(user_count_list)

    data = {
        'user_count_list': user_count_list,
        'parentclaimdata':parentclaimdata,
    }

    return render(request, "accountsview.html", data)


 
   
def accountsreview(request, ClaimNumber):
    claim = get_object_or_404(ParentModel, ClaimNumber=ClaimNumber)
    accountscomments = request.POST.get('accountscomments')

    if request.method == 'POST':
        
        new_accountstatus = request.POST.get('accountstatus')
        claim_status, created = ClaimStatus.objects.get_or_create(claim=claim)           
        claim_status.accountstatus = new_accountstatus
        claim_status.accountscomments = accountscomments
        claim_status.save() 

        user = claim.user  
        username = user.username 
        return HttpResponseRedirect(reverse('accountsview', args=(username,)))

    return render(request, "accountsview.html")


def paymentreview(request, ClaimNumber):
    claim = get_object_or_404(ParentModel, ClaimNumber=ClaimNumber)

    if request.method == 'POST':
        
        new_paymentstatus = request.POST.get('paymentstatus')         

        claim_status, created = ClaimStatus.objects.get_or_create(claim=claim) 
        claim_status.paymentstatus = new_paymentstatus   
        claim_status.save()

        user = claim.user  
        username = user.username 
        return HttpResponseRedirect(reverse('accountsview', args=(username,)))

    return render(request, "accountsview.html")  


def view_child_history(request):
    user = request.user
    parentclaimdata = ParentModel.objects.filter(user=user).order_by('-ClaimNumber')

 
    data = {
        'user': user,
        'parentclaimdata': parentclaimdata,        
    }

    return render(request, 'history.html', data)






          
     
     

    
