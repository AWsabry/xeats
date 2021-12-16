from datetime import datetime
from django.http import request
from django.shortcuts import redirect, render
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import pyrebase
import json
from .decorators import login_session_required

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
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()


db = firestore.client()


def index(request):
    return render(request, 'index.html')

def contacts(request):
    if request.method == 'POST':
        try:
            firstName = request.POST.get('firstName')
            lastName = request.POST.get('lastName')
            Email = request.POST.get('Email')
            # Password = request.POST.get('Password')
            PhoneNumber = request.POST.get('PhoneNumber')
            old_auth = firebase.auth()
            XEats_User = old_auth.create_user_with_email_and_password(
                Email, 'Password')
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

            return redirect('shop')
        except Exception as e:
            print(str(e))
    else:
        print("GETTING")
    return render(request, 'contacts.html')


@login_session_required(login_url= 'contacts')
def shop(request,):
    from google.cloud import firestore
    docs = db.collection(u'products').stream()
    auth = firebase.auth()
    passed_values = [doc.to_dict() for doc in docs]
    Email = request.session['Email']

    print(Email)

    #request.session['Email'] = Email

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


@login_session_required(login_url= 'contacts')
def productDetails(request, id):
    Email = request.session['Email']
    ProductsGet = db.collection('products').document(str(id))
    doc = ProductsGet.get().to_dict()

    userGet = db.collection('users').document(Email)
    usersdocs = userGet.get().to_dict()

    if request.method == 'POST':
        try:
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
            total = usersdocs['total'] + totalPrice

            cart = usersdocs['cart']
            cart.append(cartItem)
            print(cart)
            userGet.update({
                'cart': cart,
                'total': total
            })
            return redirect('checkout')
        except Exception as e:
            print(str(e))
    else:
        print("GETTING")

    return render(request, 'productDetails.html', {'ProductsGet': doc})


@login_session_required(login_url= 'contacts')
def checkout(request):
    Email = request.session['Email']
    OrderNote = request.POST.get('OrderNote')
    userGet = db.collection('users').document(Email)
    usersdocs = userGet.get().to_dict()
    print(Email)
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
                'Paid': False,
                'CreatedAt' :datetime.now()
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

@login_session_required(login_url= 'contacts')
def thankyou(request):
    return render(request, 'thankyou.html')

# /home/XEatsNew/X-Eats-Website