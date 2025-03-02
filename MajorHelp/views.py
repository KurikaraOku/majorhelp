from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.template import loader
from django.http import Http404
from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.views.generic import *
from django.contrib import messages
from .models import *
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
import re
from django.db.models import F, Value
from django.db.models.functions import Cast
from django.db.models import Min
from django.core.signing import TimestampSigner
from django.core.mail import send_mail
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

# Used to catch an exception if GET tries to get a value that isn't defined.
from django.utils.datastructures import MultiValueDictKeyError



def settings_view(request):
    return render(request, 'settings.html')  # Make sure you have a 'settings.html' template, or adjust accordingly

# HomeView displays the homepage
class HomeView(TemplateView):
    template_name = "MajorHelp/HomePage.html"

#University overview page 
class UniversityOverviewView(DetailView):
    model = University
    template_name = "MajorHelp/UniOverviewPage.html"
    context_object_name = "university"

    # Use slug as the lookup field
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        slug = self.kwargs['slug']
        return get_object_or_404(University, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_post_list'] = UniversityReview.objects.filter(university=self.object)
        university = self.object
        
        #JUMP
        if self.request.user.is_authenticated:
            self.request.user.refresh_from_db()
            user_review = UniversityReview.objects.filter(username=self.request.user.username, university=university).exists()
            context['user_review'] = user_review  # If review exists, pass it to the template

        
        return context
        
# View for submitting a rating to a specific catagory of a cartain university    
class SubmitRatingView(View):
    def post(self, request, pk):
        university = get_object_or_404(University, pk=pk)
        
        # Get the category and rating from the submitted form data
        category = request.POST.get('category')
        rating_value = int(request.POST.get('rating'))
        
        # Ensure the rating is between 1 and 5
        if category in ['campus', 'athletics', 'safety', 'social', 'professor', 'dorm', 'dining'] and 1 <= rating_value <= 5:
            rating, created = UniversityRating.objects.update_or_create(
                university=university,
                category=category,  # Use the selected category
                user=request.user,
                defaults={'rating': rating_value}
            )
            if created:
                messages.success(request, 'Your rating has been submitted.')
            else:
                messages.success(request, 'Your rating has been updated.')
        else:
            messages.error(request, 'Invalid rating. Please select a value between 1 and 5.')

        return redirect('MajorHelp:university-detail', slug=university.slug)

class LeaveUniversityReview(View):
    def post(self, request, username):
        review_text = request.POST.get("review_text", "").strip()
        university_id = request.POST.get("university_id")

        if not review_text:
            messages.error(request, 'Review text cannot be empty.')
            return redirect('MajorHelp:university-detail', slug=university_id)

        university = get_object_or_404(University, pk=university_id)

        # Check if the user has already left a review for this university
        existing_review = UniversityReview.objects.filter(username=request.user.username, university=university).exists()

        if existing_review:
            messages.error(request, 'You have already submitted a review for this university.')
        else:
            # Create and save the review
            UniversityReview.objects.create(
                username=request.user.username,
                review_text=review_text,
                university=university
            )
            messages.success(request, 'Your review has been successfully submitted!')

        return redirect('MajorHelp:university-detail', slug=university.slug)

# Custom form for login
class CustomLoginView(LoginView):
    def form_valid(self, form):
        remember_me = self.request.POST.get("remember_me")
        
        if not remember_me:
            # Expire session when the browser closes
            self.request.session.set_expiry(0)
        else:
            # Keep session active for 2 weeks
            self.request.session.set_expiry(1209600)  
        
        return super().form_valid(form)
    
# Custom form for SignUp
class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your Password'}), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your Password'}), label="Confirm password")
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your Email'}))
    role = forms.ChoiceField(
        choices=[('', 'Select a role')] + [choice for choice in CustomUser.ROLE_CHOICES if choice[0] != 'admin'],
        widget=forms.Select()
    )
    #NEED TO ADD FIRST NAME AND LAST NAME FIELDS
    
    class Meta:
        model = get_user_model()  # Use the custom user model dynamically
        fields = ['username', 'email', 'password', 'confirm_password', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your Username'}), #placeholder text in username box
        }
        labels = {
            'username': 'Username', # change the labe of the username entry box
        }
        help_texts = {
            'username': '', # help text by username entry box if we want to add
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.set_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()
        return user

User = get_user_model()
signer = TimestampSigner()

# SignUpView for user registration
class SignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Mark account as inactive until email verification
            user.save()

            # Generate a token that includes the user's primary key
            token = signer.sign(user.pk)
            activation_link = request.build_absolute_uri(
    reverse('MajorHelp:activate_account', args=[token])
)
            # Send an activation email to the user
            send_mail(
                'Activate Your MajorHelp Account',
                f'Please click the link to activate your account: {activation_link}',
                'noreply@majorhelp.com',  # Replace with your sender email
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'An activation email has been sent. Please check your inbox.')
            return redirect('MajorHelp:check_email')  # Redirect to login page after sign-up
        return render(request, 'registration/signup.html', {'form': form})
    

def check_email_view(request):
    return render(request, 'registration/check_email.html')

def about(request):
    return render(request, 'About/about.html')
    
def contact(request):
    return render(request,'Contact/contact.html')

def activate_account(request, token):
    try:
        # Unsign the token; valid for 1 day (86400 seconds)
        user_pk = signer.unsign(token, max_age=86400)
        user = User.objects.get(pk=user_pk)
        user.is_active = True  # Activate the user
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('MajorHelp:login')
    except SignatureExpired:
        messages.error(request, 'Activation link has expired. Please sign up again.')
        return redirect('MajorHelp:signup')
    except (BadSignature, User.DoesNotExist):
        messages.error(request, 'Invalid activation link.')
        return redirect('MajorHelp:signup')


#the search function
class SearchView(View):
    def get(self, request):
        query = request.GET.get('query', '')
        filter_type = request.GET.get('filter', 'department')
        
        # If the query is empty, reload the search page without redirecting
        if not query:
            return render(request, 'search/search.html', {'query': query, 'filter_type': filter_type})
        
        # Redirect based on the filter type if query is provided
        if filter_type == 'school':
            return redirect('MajorHelp:school_results', query=query)
        elif filter_type == 'department':
            return redirect('MajorHelp:department_results', query=query)
        elif filter_type == 'major':
            return redirect('MajorHelp:major_results', query=query)
        
        # Default behavior (in case of other filter types)
        return render(request, 'search/search.html', {'query': query, 'filter_type': filter_type})



class SchoolResultsView(View):
    def get(self, request, query):
        # Get filters from the request
        school_type = request.GET.get('school_type', 'both')  # Default to 'both'
        sort_order = request.GET.get('sort_order', 'none')  # Default to 'none'
        min_tuition = request.GET.get('min_tuition', None)
        max_tuition = request.GET.get('max_tuition', None)
        is_out_state = request.GET.get('is_out_state', 'false') == 'true'

        # Convert min_tuition and max_tuition to integers, if provided
        try:
            min_tuition = int(min_tuition) if min_tuition else None
            max_tuition = int(max_tuition) if max_tuition else None
        except ValueError:
            min_tuition = None
            max_tuition = None

        # Fetch universities matching the query
        universities = University.objects.filter(name__icontains=query)

        # Filter by school type
        if school_type == 'public':
            universities = universities.filter(is_public=True)
        elif school_type == 'private':
            universities = universities.filter(is_public=False)

        # Initialize results dictionary
        results = {}

        for university in universities:
            # Fetch associated majors
            majors = university.majors.all()

            # Determine the tuition field based on out-of-state filter
            min_tuition_field = 'out_of_state_min_tuition' if is_out_state else 'in_state_min_tuition'
            max_tuition_field = 'out_of_state_max_tuition' if is_out_state else 'in_state_max_tuition'

            # Filter majors by tuition range
            if min_tuition is not None:
                majors = majors.filter(**{f"{min_tuition_field}__gte": min_tuition})
            if max_tuition is not None:
                majors = majors.filter(**{f"{max_tuition_field}__lte": max_tuition})

            # If no majors remain after filtering, exclude the university
            if not majors.exists():
                continue

            # Collect department data
            departments = {}
            for major in majors:
                if major.department not in departments:
                    departments[major.department] = []
                departments[major.department].append(major)

            # Calculate minimum tuition for sorting
            aggregated_min_tuition = majors.aggregate(
                min_tuition=Min(min_tuition_field)
            )['min_tuition']

            # Add university details and aggregated department data to results
            results[university] = {
                'location': university.location,
                'type': 'Public' if university.is_public else 'Private',
                'departments': departments,
                'min_tuition': aggregated_min_tuition,
            }

        # Sort results by tuition if requested
        if sort_order in ['low_to_high', 'high_to_low']:
            sorted_universities = sorted(
                results.keys(),
                key=lambda uni: results[uni]['min_tuition'],
                reverse=(sort_order == 'high_to_low')
            )
            sorted_results = {uni: results[uni] for uni in sorted_universities}
        else:
            sorted_results = results

        # Render the template
        return render(request, 'search/school_results.html', {
            'query': query,
            'results': sorted_results,
            'school_type': school_type,
            'sort_order': sort_order,
            'min_tuition': min_tuition,
            'max_tuition': max_tuition,
            'is_out_state': is_out_state,
        })



class DepartmentResultsView(View):
    def get(self, request, query):
        # Get filter values from the request
        school_type = request.GET.get('school_type', 'both')  # Default to 'both'
        sort_order = request.GET.get('sort_order', 'none')  # Default to 'none'
        min_tuition = request.GET.get('min_tuition', None)  # Minimum tuition range
        max_tuition = request.GET.get('max_tuition', None)  # Maximum tuition range
        is_out_state = request.GET.get('is_out_state', 'false') == 'true'  # Check if out-of-state filter is enabled

        # Fetch majors matching the query
        majors = Major.objects.filter(department__icontains=query)

        # Filter by school type
        if school_type == 'public':
            majors = majors.filter(university__is_public=True)
        elif school_type == 'private':
            majors = majors.filter(university__is_public=False)

        # Filter by tuition range
        if min_tuition:
            tuition_field = 'out_of_state_min_tuition' if is_out_state else 'in_state_min_tuition'
            majors = majors.filter(**{f"{tuition_field}__gte": min_tuition})
        if max_tuition:
            tuition_field = 'out_of_state_max_tuition' if is_out_state else 'in_state_max_tuition'
            majors = majors.filter(**{f"{tuition_field}__lte": max_tuition})

        # Apply sorting
        if sort_order == 'low_to_high':
            majors = majors.order_by('out_of_state_min_tuition' if is_out_state else 'in_state_min_tuition')
        elif sort_order == 'high_to_low':
            majors = majors.order_by('-out_of_state_min_tuition' if is_out_state else '-in_state_min_tuition')

        # Group majors by university and department
        results = {}
        for major in majors:
            university = major.university
            if university not in results:
                results[university] = {
                    'location': university.location,
                    'type': 'Public' if university.is_public else 'Private',
                    'departments': {}
                }
            if major.department not in results[university]['departments']:
                results[university]['departments'][major.department] = []
            results[university]['departments'][major.department].append(major)

        # Render the template
        return render(request, 'search/department_results.html', {
            'query': query,
            'results': results,
            'school_type': school_type,
            'sort_order': sort_order,
            'min_tuition': min_tuition,
            'max_tuition': max_tuition,
            'is_out_state': is_out_state,
        })

class MajorResultsView(View):
    def get(self, request, query):
        # Get filters from the request
        school_type = request.GET.get('school_type', 'both')  # Default to 'both'
        sort_order = request.GET.get('sort_order', 'none')  # Default to 'none'
        min_tuition = request.GET.get('min_tuition', None)
        max_tuition = request.GET.get('max_tuition', None)
        is_out_state = request.GET.get('is_out_state', 'false') == 'true'

        # Fetch majors matching the query
        majors = Major.objects.filter(major_name__icontains=query)

        # Filter by school type
        if school_type == 'public':
            majors = majors.filter(university__is_public=True)
        elif school_type == 'private':
            majors = majors.filter(university__is_public=False)

        # Filter by tuition range
        if min_tuition:
            tuition_field = 'out_of_state_min_tuition' if is_out_state else 'in_state_min_tuition'
            majors = majors.filter(**{f"{tuition_field}__gte": min_tuition})
        if max_tuition:
            tuition_field = 'out_of_state_max_tuition' if is_out_state else 'in_state_max_tuition'
            majors = majors.filter(**{f"{tuition_field}__lte": max_tuition})

        # Apply sorting
        if sort_order == 'low_to_high':
            majors = majors.order_by('out_of_state_min_tuition' if is_out_state else 'in_state_min_tuition')
        elif sort_order == 'high_to_low':
            majors = majors.order_by('-out_of_state_min_tuition' if is_out_state else '-in_state_min_tuition')

        # Group majors by university and department
        results = {}
        for major in majors:
            university = major.university
            if university not in results:
                results[university] = {
                    'location': university.location,
                    'type': 'Public' if university.is_public else 'Private',
                    'departments': {}
                }
            if major.department not in results[university]['departments']:
                results[university]['departments'][major.department] = []
            results[university]['departments'][major.department].append(major)

        # Render the template
        return render(request, 'search/major_results.html', {
            'query': query,
            'results': results,
            'school_type': school_type,
            'sort_order': sort_order,
            'min_tuition': min_tuition,
            'max_tuition': max_tuition,
            'is_out_state': is_out_state,
        })
    
class MajorOverviewView(DetailView):
    model = Major
    template_name = "major/MajorOverviewPage.html"
    context_object_name = "major"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        major = self.object

        # Calculate the average rating for all reviews for this major
        reviews = major.major_reviews.all()
        if reviews.exists():
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            context['average_rating'] = round(average_rating, 1)  # Round to 1 decimal place
        else:
            context['average_rating'] = 0  # Default to 0 if no reviews exist

        context['reviews'] = reviews
        context['star_range'] = [1, 2, 3, 4, 5]

        #JUMP
        # Check if the user has already left a review for this major
        if self.request.user.is_authenticated:
            user_review = MajorReview.objects.filter(user=self.request.user, major=major).first()
            context['user_review'] = user_review  # If review exists, pass it to the template

        return context


class CalcView(View):
    def get(self, request):
        # TODO(jpreuss) Pass the json back to the frontend to prepopulate
        #               the already filled data.
        return render(request, 'calc/calc.html')

# Flag for the backend to tell the front that it doesn't exist.
DNE = "DOESNOTEXIST"

class CalcInfo(View):
    def get(self, request):
        
        # Check to see if there are no entries in the GET request, if so, its
        # likely because the user is accessing /calc/info on their browser directly.
        if not request.GET:

        # if so then just redirect to the calculator
            return HttpResponseRedirect(reverse("MajorHelp:calc"))
        


        inData = {}
        try: 
            inData = {
                "university" : request.GET['uni'],          # required
                "outstate"   : request.GET['outstate'],
                "department" : request.GET['dept'],
                "major"      : request.GET['major'],        # required
                "aid"        : request.GET['aid'],
            }
        
        # This exception is raised if one of the values (uni, dept, etc) is not defined.
        # Effectively, this saves me from having to do an if with DeMorgan's law on every
        # single data value.
        #
        # If there isn't a value defined yet, then for some reason the front end did not
        # validate the get json, return a 400 - Bad Request
        except MultiValueDictKeyError as e:
            
            # \u0002 (␂) aka start of text will be used in case the front end needs to
            # skip any header and get to the 'str(e)' that contains the malformated
            # (likely null) entry.
            return HttpResponseBadRequest("<h1> 400 Bad Request </h1><br>\u0002" + str(e) + " is not defined.")


        # Prepare the output JSON

        # Get whether the student is instate or out of state     
        outstate = inData["outstate"] == "true"

        # Get the university.

        # University is a required entry
        if inData["university"] == "":
            return HttpResponseBadRequest("<h1> 400 Bad Request </h1><br>\u0002 'uni' is left blank.")


        university = {
            "name"          : None,
            "baseMinTui"    : 0,
            "baseMaxTui"    : 0,
            "fees"          : 0,
        }


        # For now we'll have to rely on the user inputting the name of the university exactly.
        uniObj = None
        try:
            uniObj = University.objects.get(name__iexact=inData["university"])

        except University.DoesNotExist as error:
            # print("No university of name: \"" + inData["university"] + "\" was found.")

            university["name"] = DNE
        else:
            # get the data for the university

            university["name"]  = uniObj.name

            university["baseMinTui"] = uniObj.out_of_state_base_min_tuition if outstate else uniObj.in_state_base_min_tuition
            university["baseMaxTui"] = uniObj.out_of_state_base_max_tuition if outstate else uniObj.in_state_base_max_tuition

            university["fees"] = uniObj.fees


        # Get the Major

        # Major is a required entry
        if inData["major"] == "":
            return HttpResponseBadRequest("<h1> 400 Bad Request </h1><br>\u0002 'major' is left blank.")


        major = {
            "name"          : None,
            "uni"           : None,
            "baseMinTui"    : 0,
            "baseMaxTui"    : 0,
            "fees"          : 0,
        }


        majorObj = None
        try: 
            majorObj = Major.objects.get(major_name__iexact=inData["major"])

        except Major.DoesNotExist as error:
            # print("No major of name: \"" + inData["major"] + "\" was found.")

            major["name"] = DNE
        else: 
            # get the data for the majo

            major["name"] = majorObj.major_name

            major["uni"] = majorObj.university.name

            major["baseMinTui"] = majorObj.out_of_state_min_tuition if outstate else majorObj.in_state_min_tuition
            major["baseMaxTui"] = majorObj.out_of_state_max_tuition if outstate else majorObj.in_state_max_tuition

            major["fees"] = majorObj.fees


        # setup financial aid

        aid = {
            "name"          : "",
            "amount"        : 0,
        }


        if (inData["aid"] != ""):
            aidObj = None
            try:
                aidObj = FinancialAid.objects.get(name__iexact=inData["aid"])
            except FinancialAid.DoesNotExist as error:
                # print("No financial aid of name: \"" + inData["aid"] + "\" was found.")

                aid["name"] = DNE
            else:
                # get the data for Financial aid
                aid["name"] = aidObj.name

                aid["amount"] = aidObj.amount




        outData = {
            "minTui"        : 0,
            "maxTui"        : 0,
            "outstate"      : False,
            "uni"           : university,
            "major"         : major,
            "aid"           : aid,
            # Any extra data can either go here or in Alerts.
            "Alerts"     : {},    # Kept for aspirational purposes
        }


        outData['outstate'] = outstate

        # calculate the final tuition range

        outData["minTui"] = university["baseMinTui"] + university["fees"]   + \
                            major["baseMinTui"] + major["fees"]               \
                            - aid["amount"]

        outData["maxTui"] = university["baseMaxTui"] + university["fees"]   + \
                            major["baseMaxTui"] + major["fees"]               \
                            - aid["amount"]
        

        return JsonResponse(outData)


# LeaveMajorReview View - Exclusive for leaving reviews for a major at a specific school

@login_required
def LeaveMajorReview(request, slug):
    major = get_object_or_404(Major, slug=slug)

    # Check if the form is submitted via POST
    if request.method == 'POST':
        # Get the review text and rating from the form
        review_text = request.POST.get('review_text')
        rating = request.POST.get('rating')  # Get the selected rating (1-5)

        if not (1 <= int(rating) <= 5):
            messages.error(request, 'Please provide a valid rating between 1 and 5.')
            return redirect('MajorHelp:major-detail', slug=slug)

        # Create and save the review using the MajorReview model
        MajorReview.objects.create(
            major=major,
            user=request.user,  # Use request.user which is a User object
            review_text=review_text,
            university=major.university,  # Link the university associated with the major
            rating=rating  # Save the rating
        )

        messages.success(request, 'Your review has been successfully submitted!')
        return redirect('MajorHelp:major-detail', slug=slug)

    return render(request, 'leave_review.html', {'major': major})

# Render review stars in Major Overview
class UniversityRequestView(View):
    def get(self, request):
        return render(request, 'search/universityRequest.html')

    def post(self, request):
        request_text = request.POST.get('request_text')
        if request_text:
            UniversityRequest.objects.create(
                user=request.user if request.user.is_authenticated else None,
                request_text=request_text
            )
            messages.success(request, 'Your university request has been submitted.')
            return redirect('MajorHelp:home')
        else:
            messages.error(request, 'Please enter your request.')
            return render(request, 'search/universityRequest.html')
    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import University

@csrf_exempt
def university_search(request):
    query = request.GET.get('query', '')

    if not query:
        return JsonResponse({"error": "No search query provided"}, status=400)

    universities = University.objects.filter(name__icontains=query)

    if not universities.exists():
        return JsonResponse({"error": "No university found"}, status=404)

    data = {"universities": []}
    for uni in universities:
        data["universities"].append({
            "name": uni.name,
            "location": uni.location,
            "departments": list(uni.majors.values_list("department", flat=True).distinct()),
        })

    return JsonResponse(data)
def major_list(request):
    university_name = request.GET.get('university', '')
    department = request.GET.get('department', '')

    # Ensure university exists
    university = University.objects.filter(name__icontains=university_name).first()
    if not university:
        return JsonResponse({"error": "University not found"}, status=404)

    # Filter majors by university and department
    majors = Major.objects.filter(university=university, department=department)
    if not majors.exists():
        return JsonResponse({"majors": []})  # Return empty list if no majors found

    data = {"majors": [{"name": major.major_name} for major in majors]}
    return JsonResponse(data)
def major_info(request):
    university_name = request.GET.get('university', '')
    major_name = request.GET.get('major', '')
    outstate = request.GET.get('outstate', 'false') == 'true'

    # Ensure university exists
    university = University.objects.filter(name__icontains=university_name).first()
    if not university:
        return JsonResponse({"error": "University not found"}, status=404)

    # Ensure major exists
    major = Major.objects.filter(university=university, major_name__icontains=major_name).first()
    if not major:
        return JsonResponse({"error": "Major not found"}, status=404)

    # Determine correct tuition range
    if outstate:
        min_tuition = university.out_of_state_base_min_tuition + major.out_of_state_min_tuition
        max_tuition = university.out_of_state_base_max_tuition + major.out_of_state_max_tuition
    else:
        min_tuition = university.in_state_base_min_tuition + major.in_state_min_tuition
        max_tuition = university.in_state_base_max_tuition + major.in_state_max_tuition

    data = {
        "uni": {
            "name": university.name,
            "baseMinTui": university.in_state_base_min_tuition if not outstate else university.out_of_state_base_min_tuition,
            "baseMaxTui": university.in_state_base_max_tuition if not outstate else university.out_of_state_base_max_tuition,
            "fees": university.fees
        },
        "major": {
            "name": major.major_name,
            "baseMinTui": major.in_state_min_tuition if not outstate else major.out_of_state_min_tuition,
            "baseMaxTui": major.in_state_max_tuition if not outstate else major.out_of_state_max_tuition,
            "fees": major.fees
        },
        "minTui": min_tuition,
        "maxTui": max_tuition
    }

    return JsonResponse(data)
