from django.shortcuts import redirect, render
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import pyrebase
import json
from Website.decorators import login_session_required, verify_mode_required, refresh_session, no_access_for_login, no_cart_access
from twilio.rest import Client
import random
from django.template.loader import render_to_string
from django.contrib import messages
from firebase_admin import auth
from django.core.mail import EmailMessage
from X_Eats import settings

# Create your views here.


cred = credentials.Certificate(
    "x-eats-4a034-firebase-adminsdk-7rdrx-329e05b70d.json")

firebaseConfig = {
    'apiKey': "AIzaSyAQpbI7MDkObxXnHkcwQ7wNGqT3i-wIVic",
    'authDomain': "x-eats-4a034.firebaseapp.com",
    'databaseURL': "https://x-eats-4a034-default-rtdb.firebaseio.com",
    'projectId': "x-eats-4a034",
    'storageBucket': "x-eats-4a034.appspot.com",
    'messagingSenderId': "900670833493",
    'appId': "1:900670833493:web:b3dcee553a6ff88090e5dc",
    'measurementId': "G-93L34JXS0F"

}
try:
    app = firebase_admin.get_app()
except ValueError as e:
    firebase_admin.initialize_app(cred)
    
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
db = firestore.client()

@refresh_session(None, *['verify'])
def index(request):
    return render(request, 'index.html')

@no_access_for_login(login_url='shop')
@refresh_session(None, *['verify'])
def contacts(request):
    if request.session.get('verify'):
        del request.session['verify']
    
    if request.method == 'POST':
        firstName =request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        Email = request.POST.get('Email').lower() 
        Password = request.POST.get('Password')
        Password_Confirmation = request.POST.get('Password_Confirmation')
        otp = random.randint(1000,9999)
        try:
            user = auth.get_user_by_email(Email)
        except:
            if Password != Password_Confirmation:
                messages.error(request, 'The password confirmation mismatch' , extra_tags='danger')
                return redirect('contacts')
            
            # send an email
            subject = 'Activate user account'
            body = render_to_string('activate.html', {
                'user':f'{firstName} {lastName}',
                'otp':otp
            })
            email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [Email])
            email.send()
                
            messages.success(request, f'There is an email has been sent to {Email}.')
            #put verify data to session
            request.session['verify'] = {'otp':otp, 'data':request.POST}
            return redirect('email_verify')
        else:
            messages.error(request, 'This email already exits!' , extra_tags='danger')
            if Password != Password_Confirmation:
                messages.error(request, 'The password confirmation mismatch' , extra_tags='danger')
            return redirect('contacts')
        
    return render(request, 'contacts.html')

@login_session_required(login_url='contacts')
def shop(request):
    from google.cloud import firestore
    docs = db.collection(u'products').stream()
    auth = firebase.auth()
    passed_values = [doc.to_dict() for doc in docs]
    Email = request.session['Email']

    for i in passed_values:
        id = i['id']
        productName = i['name']
        price = i['price']
        category = i['category']

    if request.method == 'POST':
        redirect('productDetails', {'id': id, })
    return render(request, 'shop.html', {
        "docs": passed_values,
    })

@login_session_required(login_url='contacts')
def productDetails(request, id):
    Email = request.session['Email']
    ProductsGet = db.collection('products').document(str(id))
    doc = ProductsGet.get().to_dict()

    userGet = db.collection('users').document(Email)
    usersdocs = userGet.get().to_dict()
    if request.method == 'POST':
        # try:
        Quantity = request.POST.get('Quantity')
        request.session['Email'] = Email
        cartItem = {
            'ProductName': doc['name'],
            'Quantity': int(Quantity),
            'Price': doc['price'],
            'Category': doc['category'],
            'ProductID': doc['id']
        }

        totalPrice = int(Quantity) * doc['price']
        total = usersdocs.get('total') + totalPrice if usersdocs.get('total') else totalPrice

        cart = usersdocs['cart']
        cart.append(cartItem)
        userGet.update({
            'cart': cart,
            'total': total
        })
        return redirect('checkout')
        # except Exception as e:
            # print(str(e))
    else:
        print("GETTING")

    return render(request, 'productDetails.html', {'ProductsGet': doc})

@no_cart_access(db, test_func=None, login_url='shop')
@login_session_required(login_url='contacts')
def checkout(request):
    Email = request.session['Email']
    OrderNote = request.POST.get('OrderNote')
    userGet = db.collection('users').document(Email)
    usersdocs = userGet.get().to_dict()
    print(userGet.get().to_dict()['cart'])
    if request.method == 'POST':
        try:
            firstName = usersdocs['firstName']
            lastName = usersdocs['lastName']
            PhoneNumber = usersdocs['PhoneNumber']
            cart = usersdocs['cart']
            total = usersdocs['total']
            ID = uuid.uuid4()
            new_doc_ref = db.collection('orders').document(str(ID))
            new_doc_ref.set({
                'firstName': firstName,
                'lastName': lastName,
                'Email': Email,
                'price': total + 5,
                'PhoneNumber': PhoneNumber,
                'OrderNote': OrderNote,
                'cart': cart,
                'Ordered': False
            }),
            userGet.update({
                'cart': [],
                'total': 0
            })
            return redirect('thankyou')
        except Exception as e:
            print(str(e))
    else:
        print("GETTING")
    return render(request, 'checkout.html',{'usersdocs': usersdocs})

@login_session_required(login_url='index')
def thankyou(request):
    return render(request, 'thankyou.html')

@verify_mode_required(login_url='contacts')
def send_activate_mail(request):
    if request.method == 'POST':
        # getting user data from session 
        data = request.session['verify']
        firstName =data['data'].get('firstName')
        lastName = data['data'].get('lastName')
        Email = data['data'].get('Email').lower()
        Password = data['data'].get('Password')
        PhoneNumber = data['data'].get('PhoneNumber')
        
        otp = request.POST.get('otp')
        if data.get('otp') == int(otp):
            old_auth = firebase.auth()
            XEats_User = old_auth.create_user_with_email_and_password(
                Email, Password)
            user = old_auth.refresh(XEats_User['refreshToken'])
            ID = uuid.uuid4()
            request.session['Email'] = Email
            new_doc_ref = db.collection('users').document(Email)
            new_doc_ref.set({
                'firstName': firstName,
                'lastName': lastName,
                'Email & ID': Email,
                'total': 0,
                'PhoneNumber': PhoneNumber,
                'cart': [],
            }),
            del request.session['verify']
            return redirect('shop')
        messages.error(request,'The code is not correct try again.' , extra_tags='danger')
    return render(request, 'email_verify.html')

@refresh_session(None, *['Email'])
def logout(request):
    return redirect('index')

@no_access_for_login(login_url='index')
def login(request):
    if request.method == 'POST':
        Email = request.POST.get('Email').lower() 
        Password = request.POST.get('Password')
        
        try:
            user = firebase.auth().sign_in_with_email_and_password(email=Email, password=Password)
        except:
            messages.error(request, 'The inputs are invalid!' , extra_tags='danger')
            return redirect('login')
        else:
            request.session['Email'] = Email
            return redirect('shop')
        print(user)
    return render(request, 'login.html')


def reset_cart(request):
    Email = request.session['Email']
    userGet = db.collection('users').document(Email)
    usersdocs = userGet.set({'cart':[]})
    
    return redirect('shop')
