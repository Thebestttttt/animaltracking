from animaltracking.models import *
from django.urls import reverse
import json
from django.contrib.auth.models import *
from django.shortcuts import *
from django.db.models import *
from django.db.models.functions import  *
from .forms import *
from django.db import transaction
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages


#เช็คว่าสัตว์ตัวนี้เป็นของ user นี้ไหม
def is_my_animal(user, animal):
    # ถ้าเป็นสัตว์หาย
    if LostAnimal.objects.filter(animal=animal, reported_by=user).exists():
        return True
    
    # ถ้าเป็นสัตว์จรจัด
    if StrayAnimal.objects.filter(animal=animal, reported_by=user).exists():
        return True
    
    return False

# สร้าง user
@transaction.atomic
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        form_profile = ProfileForm(request.POST)
        try:
            with transaction.atomic():
                if form.is_valid() and form_profile.is_valid():
                    user = form.save()
                    profile = form_profile.save(commit=False)
                    profile.user = user
                    profile.save()

                    # เพิ่ม user เข้า group user
                    usergrup = Group.objects.get(name='User')
                    user.groups.add(usergrup)        
                    
                    # login อัตโนมัติหลังสมัคร
                    login(request, user)
                    return redirect("home")
                else:
                    raise transaction.TransactionManagementError("Form is not valid")
        except Exception as e:
            print(form.errors, form_profile.errors)
            print(e)
            # rollback
            return render(request, "signup.html", {"form": form, "form_profile": form_profile, "error": str(e)})
    else:
        form = CustomUserCreationForm()
        form_profile = ProfileForm()
    return render(request, "signup.html", {"form": form, "form_profile": form_profile})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # return redirect("home")
            nexturl = request.POST.get('next')
            if nexturl:
                return redirect(nexturl)
            else:
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request) #ลบ session ที่login ไว้ออก
    return redirect("login")

@login_required
def Change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # บันทึก session ใหม่ ไม่ให้เด้งออกไปlogin
            messages.success(request, 'change password successfully')
            return redirect('home')
        else:
            messages.error(request, 'please correct the error')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def HomeView(request):
    if request.method == "GET":
        stray_animals = StrayAnimal.objects.all()
        lost_animals = LostAnimal.objects.all()

        data = []

        for s in stray_animals:
            data.append({
                "type": "stray",
                "animal_name": s.animal.name,
                "species": s.animal.species,
                "lat": s.latitude,
                "long": s.longitude,
                # reverse ป้องกันการเขียน url ผิด
                "url": reverse("stray_comment", args=[s.pk])
            })

        for l in lost_animals:
            data.append({
                "type": "lost",
                "animal_name": l.animal.name,
                "species": l.animal.species,
                "lat": l.latitude,
                "long": l.longitude,
                "status": l.status,
                "url": reverse("lost_comment", args=[l.pk])
            })
    return render(request, "home.html" , {"data": json.dumps(data)})



@permission_required("animaltracking.view_strayanimal", login_url='login')
def StrayView(request):
    if request.method == "GET":
        stray_animals = StrayAnimal.objects.all()

        # filter 
        search_txt = request.GET.get("search", "")
        filter_type = request.GET.get("filter", "")

        animal_list = Animal.objects.all()
        if search_txt:
            if filter_type == "species":
                animal_list = animal_list.filter(species__icontains=search_txt)
            elif filter_type == "gender":
                animal_list = animal_list.filter(gender__icontains=search_txt)

        # แปลงข้อมูล stray_animals สำหรับ map 
        data = []
        for s in stray_animals:
            data.append({
                "type": "stray",
                "animal_name":  s.animal.name,
                "species":  s.animal.species,
                "lat":  s.latitude,
                "long":  s.longitude,
                "url": reverse("stray_comment", args=[s.pk])
            })

    return render(request, "stray_list.html", {"data": json.dumps(data),"stray_animals": stray_animals,"filter": filter_type,"search": search_txt})

    
@permission_required("animaltracking.add_strayanimal", login_url='login')
@transaction.atomic
def CreateStrayAnimalView(request):
    if request.method == "POST":
        form_animal = AnimalForm(request.POST, request.FILES)
        form_stray = StrayAnimalForm(request.POST, request.FILES)
        try:
            with transaction.atomic():
                if form_animal.is_valid():
                    animal = form_animal.save()
                    #ดึงข้อมูล animal.id มาใส่ใน form_stray
                    form_stray = StrayAnimalForm(
                        data={**request.POST.dict(), "animal": animal.id},
                        files=request.FILES
                    )
                    if form_stray.is_valid():
                        stray = form_stray.save(commit=False)
                        stray.reported_by = request.user
                        stray.save()
                    else:
                        raise transaction.TransactionManagementError("StrayAnimal form is not valid")
                else:
                    raise transaction.TransactionManagementError("Animal form is not valid")
            return redirect("stray")
        except Exception as e:
            print(form_animal.errors, form_stray.errors)
            print(e)
            # rollback
            return render(request, "stray_create.html", {"form_animal": form_animal, "form_stray": form_stray, "error": str(e)})
    else:
        form_animal = AnimalForm()
        form_stray = StrayAnimalForm()
    return render(request, "stray_create.html", {"form_animal": form_animal, "form_stray": form_stray})


@permission_required("animaltracking.change_strayanimal", login_url='login')
@transaction.atomic
def EditStrayView(request, pk):
    stray_animal = get_object_or_404(StrayAnimal, pk=pk)
    animal = stray_animal.animal

    if request.method == "POST":
        form_animal = AnimalForm(request.POST, request.FILES, instance=animal)
        form_stray = StrayAnimalForm(request.POST, request.FILES, instance=stray_animal)
        if not is_my_animal(request.user, animal):
            messages.error(request, "คุณไม่มีสิทธิ์แก้ไขข้อมูลสัตว์นี้")
            return redirect("stray_edit", pk=pk) 
        try:
            with transaction.atomic():
                if form_animal.is_valid():
                    animal = form_animal.save()
                    form_stray = StrayAnimalForm(
                        data={**request.POST.dict(), "animal": animal.id},
                        files=request.FILES,
                        instance=stray_animal
                    )
                    if form_stray.is_valid():
                        stray = form_stray.save(commit=False)
                        stray.save()
                    else:
                        raise transaction.TransactionManagementError("StrayAnimal form is not valid")
                else:
                    raise transaction.TransactionManagementError("Animal form is not valid")
            return redirect("stray_edit", pk=pk) 
        except Exception as e:
            print(form_animal.errors, form_stray.errors)
            print(e)
            # rollback
            return render(request, "stray_edit.html", {"form_animal": form_animal, "form_stray": form_stray, "error": str(e)})
    else:
        form_animal = AnimalForm(instance=animal)
        form_stray = StrayAnimalForm(instance=stray_animal)
    return render(request, "stray_edit.html", {"form_animal": form_animal, "form_stray": form_stray})

@permission_required("animaltracking.delete_strayanimal", login_url='login')
def DeleteStrayView(request, pk):
    stray_animal = get_object_or_404(StrayAnimal, pk=pk)
    animal = stray_animal.animal
    if request.method == "POST":
        animal.delete()
        return redirect("stray")
    return render(request, "stray_list.html", {"stray_animal": stray_animal})

@permission_required("animaltracking.add_comment", login_url='login')
@transaction.atomic
def CommentStrayView(request, pk):
    stray_animal = get_object_or_404(StrayAnimal, pk=pk)
    animal = stray_animal.animal
    tag = animal.tag.all()
    users = stray_animal.reported_by
    profile = Profile.objects.get(user=users)

    data = []
    data.append({
        "type": "stray",
        "animal_name":  stray_animal.animal.name,
        "species":  stray_animal.animal.species,
        "lat":  stray_animal.latitude,
        "long":  stray_animal.longitude,
        "url": reverse("stray_comment", args=[stray_animal.pk])
    })

    # ดึง comments ทั้งหมดของสัตว์ตัวนี้
    comments = Comment.objects.filter(animal=animal).order_by("comment_date")

    if request.method == "POST":
        form_comment = CommentForm(request.POST)
        try:
             with transaction.atomic():
                if form_comment.is_valid():
                    comment = form_comment.save(commit=False)
                    comment.animal = animal
                    comment.comment_by = request.user 
                    comment.save()
                    return redirect("stray_comment", pk=pk)
                else:
                    raise transaction.TransactionManagementError("Comment form is not valid")
        except Exception as e:
            print(form_comment.errors)
            print(e)
            # rollback
            return render(request, "stray_comment.html", {
                "animal": animal,
                "stray_animal": stray_animal,
                "comments": comments,
                "tag": tag,
                "profile": profile,
                "form_comment": form_comment,
                "data": json.dumps(data),
                "error": str(e)
            })
    else:
        form_comment = CommentForm()

    return render(request, "stray_comment.html", {
        "animal": animal,
        "stray_animal": stray_animal,
        "comments": comments,
        "tag": tag,
        "profile": profile,
        "form_comment": form_comment,
        "data": json.dumps(data)})




@permission_required("animaltracking.view_lostanimal", login_url='login')
def LostView(request):
    if request.method == "GET":
        # order by เอาlostขึ้นก่อน
        lost_animals = LostAnimal.objects.all().annotate(status_order=Case(
            When(status='Lost', then=Value(0)),
            When(status='Found', then=Value(1)),
            output_field=IntegerField()
        )).order_by('status_order')

        #  filter
        search_txt = request.GET.get("search", "")
        filter_type = request.GET.get("filter", "")

        animal_list = Animal.objects.all()
        if search_txt:
            if filter_type == "species":
                animal_list = animal_list.filter(species__icontains=search_txt)
            elif filter_type == "gender":
                animal_list = animal_list.filter(gender__icontains=search_txt)
        
        # แปลงข้อมูล stray_animals สำหรับ map 
        data = []
        for l in lost_animals:
            data.append({
                "type": "lost",
                "animal_name": l.animal.name,
                "species": l.animal.species,
                "lat": l.latitude,
                "long": l.longitude,
                "status": l.status,
                "url": reverse("lost_comment", args=[l.pk])
            })
    return render(request, "lost_list.html", {
        "data": json.dumps(data),
        "lost_animals": lost_animals,
        "filter": filter_type,
        "search": search_txt
    })

@permission_required("animaltracking.add_lostanimal", login_url='login')
@transaction.atomic
def CreateLostAnimalView(request):
    if request.method == "POST":
        form_animal = AnimalForm(request.POST, request.FILES)
        form_lost = LostAnimalForm(request.POST, request.FILES)
        try:
            with transaction.atomic():
                if form_animal.is_valid():
                    animal = form_animal.save()
                    form_lost = LostAnimalForm(
                        data={**request.POST.dict(), "animal": animal.id},
                        files=request.FILES
                    )
                    if form_lost.is_valid():
                        lost = form_lost.save(commit=False)
                        lost.reported_by = request.user 
                        lost.save()
                    else:
                        raise transaction.TransactionManagementError("LostAnimal form is not valid")
                else:
                    raise transaction.TransactionManagementError("Animal form is not valid")
            return redirect("lost")
        except Exception as e:
            print(form_animal.errors, form_lost.errors)
            print(e)
            # rollback
            return render(request, "lost_create.html", {"form_animal": form_animal, "form_lost": form_lost, "error": str(e)})
    else:
        form_animal = AnimalForm()
        form_lost = LostAnimalForm()
    return render(request, "lost_create.html", {"form_animal": form_animal, "form_lost": form_lost})

@permission_required("animaltracking.change_lostanimal", login_url='login')
def EditLostView(request, pk):
    lost_animal = get_object_or_404(LostAnimal, pk=pk)
    animal = lost_animal.animal

    if request.method == "POST":
        form_animal = AnimalForm(request.POST, request.FILES, instance=animal)
        form_lost = LostAnimalForm(request.POST, request.FILES, instance=lost_animal)
        if not is_my_animal(request.user, animal):
            messages.error(request, "คุณไม่มีสิทธิ์แก้ไขข้อมูลสัตว์นี้")
            return redirect("lost_edit", pk=pk)
        try:
            with transaction.atomic():
                if form_animal.is_valid():
                    animal = form_animal.save()
                    form_lost = LostAnimalForm(
                        data={**request.POST.dict(), "animal": animal.id},
                        files=request.FILES,
                        instance=lost_animal
                    )
                    if form_lost.is_valid():
                        lost = form_lost.save(commit=False)
                        lost.save()
                    else:
                        raise transaction.TransactionManagementError("LostAnimal form is not valid")
                else:
                    raise transaction.TransactionManagementError("Animal form is not valid")
            return redirect("lost_edit", pk=pk) 
        except Exception as e:
            print(form_animal.errors, form_lost.errors)
            print(e)
            # rollback
            return render(request, "lost_edit.html", {"form_animal": form_animal, "lost_animal": form_lost, "error": str(e)})
    else:
        form_animal = AnimalForm(instance=animal)
        form_lost = LostAnimalForm(instance=lost_animal)
    return render(request, "lost_edit.html", {"form_animal": form_animal, "form_lost": form_lost})

@permission_required("animaltracking.delete_lostanimal", login_url='login')
def DeleteLostView(request, pk):
    lost_animal = get_object_or_404(LostAnimal, pk=pk)
    animal = lost_animal.animal

    if request.method == "POST":
        animal.delete()
        return redirect("lost")
    return render(request, "lost_list.html")

@permission_required("animaltracking.add_comment", login_url='login')
@transaction.atomic
def CommentLostView(request, pk):
    lost_animal = get_object_or_404(LostAnimal, pk=pk)
    animal = lost_animal.animal
    tag = animal.tag.all()
    users = lost_animal.reported_by
    profile = Profile.objects.get(user=users)

    data = []
    data.append({
        "type": "lost",
        "animal_name":  lost_animal.animal.name,
        "species":  lost_animal.animal.species,
        "lat":  lost_animal.latitude,
        "long":  lost_animal.longitude,
        "url": reverse("lost_comment", args=[lost_animal.pk])
    })

    # ดึง comments ทั้งหมดของสัตว์ตัวนี้
    comments = Comment.objects.filter(animal=animal).order_by("comment_date")

    if request.method == "POST":
        form_comment = CommentForm(request.POST)
        try:
            with transaction.atomic():
                if form_comment.is_valid():
                    comment = form_comment.save(commit=False)
                    comment.animal = animal
                    comment.comment_by = request.user 
                    comment.save()
                    return redirect("lost_comment", pk=pk)
                else:
                    raise transaction.TransactionManagementError("Comment form is not valid")
        except Exception as e:
                print(form_comment.errors)
                print(e)
                # rollback
                return render(request, "lost_comment.html", {
                    "animal": animal,
                    "lost_animal": lost_animal,
                    "comments": comments,
                    "tag": tag,
                    "profile": profile,
                    "form_comment": form_comment,
                    "data": json.dumps(data),
                    "error": str(e)
                })
    else:
        form_comment = CommentForm()

    return render(request, "lost_comment.html", {
        "animal": animal,
        "lost_animal": lost_animal,
        "comments": comments,
        "tag": tag,
        "profile": profile,
        "form_comment": form_comment,
        "data": json.dumps(data)
    })


@permission_required("animaltracking.delete_comment", login_url='login')
def DeleteCommentStrayView(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    animal = comment.animal
    stray_animal = StrayAnimal.objects.get(animal=animal)

    if request.method == "POST":
        comment.delete()
        return redirect("stray_comment", pk=stray_animal.id)

    return render(request, "stray_comment.html", {"comment": comment})

@permission_required("animaltracking.delete_comment", login_url='login')
def DeleteCommentLostView(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    animal = comment.animal
    lost_animal = LostAnimal.objects.get(animal=animal)
    

    if request.method == "POST":
        comment.delete()
        return redirect("lost_comment", pk=lost_animal.id)

    return render(request, "lost_comment.html", {"comment": comment})

@permission_required("animaltracking.view_tag", login_url='login')
def ManageTagView(request):
    tags = Tag.objects.all()

    # เพิ่ม tag
    if request.method == "POST":
        form = TagForm(request.POST)  # ชื่อตรงกับ template
        if form.is_valid():
            form.save()
            return redirect("manage_tag")
    else:
        form = TagForm()
    return render(request, "manage_tag.html", {"tags": tags, "form": form})

@permission_required("animaltracking.delete_tag", login_url='login')
def DeleteTagView(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == "POST":
        tag.delete()
        return redirect("manage_tag")

    return render(request, "manage_tag.html", {"tag": tag})
