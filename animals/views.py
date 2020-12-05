from django.http import request
from django.http.response import JsonResponse
from animals.models import Animal, Donation, Wish
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic import ListView
from images.models import Image
from mailer import mailer

# For root URL (homepage):

# 'as_view()' method will return the defined query set as context object
class ActiveWishList(ListView):
    # Below is same as 'queryset = Wish.objects.all()'
    # model = Wish
    
    queryset = Wish.objects.filter(active=True)
    context_object_name = 'active_wish_list'

# Return list of active wishes; each list item has picture of animal, button to donate, and link to detail page
# def ActiveWishList(request):
#     wishes = Wish.objects.all()    
#     print(wishes)
    
#     return HttpResponse('This is the homepage.')


# class IndexView(generic.ListView):
#     model = Animal
#     template_name = 'animals/index.html'
#     context_object_name = 'animals_index'
    
#     def get_queryset(self):
#         return Animal.objects.all
    
# Index using functional view instead of class based    
def index(request):
    # Use pagination/React components once page gets big enough
    animals_list = Animal.objects.all()
    
    return render(request, 'animals/index.html', {'animals_list': animals_list})

def detail(request, animal_id):
    # animal = Animal.objects.get(pk=animal_id)
    # # return JsonResponse({animal})
    # return HttpResponse(animal)

    # get_object_or_404 does what it says
    animal = get_object_or_404(Animal, pk=animal_id)
    
    # Below method is same as 'get_object_or_404' method above
    # try:
    #     animal = Animal.objects.get(pk=animal_id)
    # except Animal.DoesNotExist:
    #     raise Http404("Animal does not exist")
    # return render(request, 'animals/detail.html', {'animal': animal})
    
    # render method uses template in '/animals/templates' to return HTML template
    return render(request, 'animals/detail.html', {'animal': animal})

# Create donation with parameters from POST request (default user and amount for now)
# Needs to do something with donor info from request Ex: 
def donate(request, animal_id):
    
    print (f'The request was: {request}')
    print (request.POST)
    animal = get_object_or_404(Animal, pk=animal_id)
    wish = get_object_or_404(Wish, pk=request.POST['wish_id'])

    try:
        d = Donation(
                wish_id=request.POST['wish_id'], 
                first_name=request.POST['first_name'], 
                last_name=request.POST['ast_name'],
                email=request.POST['email'],
                amount=request.POST['amount']
            )
        mailer.send_recpt(d)
        if d.save():
            if wish.current_funding() >= wish.fund_amount:
                wish.complete_funding()
                wish.save()
            d.save()
        print (f'{d.user} donated {d.amount} to {d.wish}')
    except (KeyError, Wish.DoesNotExist):
        return render(request, 'animals/detail.html', {'animal': animal, 'error_message': 'Please select a wish'})
    else:
        # reverse() is a utility function provided by Django
        return HttpResponseRedirect(reverse('animals:detail', args=(animal.id,)))
    
# /animals/:animal_id/wish
# Maybe refactor into separate wish app and use '/wishes/:wish_id
# Method is for updating active wish with pictures, not creating new wish
def update_wish(request, animal_id):
    # Get active wish from animal's set
    # GET returns form to upload images (no other attribute changes)
    # POST adds images and triggers mailer to send email with images to donor
    
    animal = Animal.objects.get(pk=animal_id)
    wish = animal.get_active_wish()
    if request.POST:
        img = Image.objects.create(upload=request.POST[''])
        wish.images.add(img)
        mailer.send_donor_imgs(wish)
    else:
        # Are these doing the same thing?
        # return render(request, 'animals/detail.html', {'animal': animal})
        # return HttpResponseRedirect(reverse('animals:detail', args=(animal.id,)))
        return render(request, 'animals/wish_form.html', {'wish': wish})