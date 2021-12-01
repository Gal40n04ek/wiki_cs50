import re
import markdown2
import random, secrets

from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from . import util
from markdown2 import Markdown

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", widget = forms.TextInput(attrs={"class":"form-control col-md-6 col-lg-4"}))
    content = forms.CharField(label="Content", widget = forms.Textarea(attrs={"class": "form-control col-md-12 col-lg-10", "rows": 20}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def add(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            for entry in util.list_entries():
                if title.upper() == entry.upper():
                    title = entry;
            if util.get_entry(title) is None:
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", kwargs={"entry":title}))
            else:
                return render (request, "encyclopedia/add.html", {
                    "form": form,
                    "adder_checker": True,
                    "entry": title
                })
        else:
            return render(request, "encyclopedia/add.html", {
                "form": form
            })
    return render(request, "encyclopedia/add.html", {
        "form": NewEntryForm()
    })

def edit (request, entry):
    if request.method == 'GET':
        entryPage = util.get_entry(entry);
        form = NewEntryForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        if entryPage is None:
            return render(request, "encyclopedia/non_exist.html", {
                "entryTitle": entry
            })
        else:
            return render(request,"encyclopedia/edit.html", {
                "form":form,
            })
    if request.method == 'POST':
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]        
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("entry", kwargs={"entry":title}))

def entry (request, entry):
    markdowner = Markdown()
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/non_exist.html", {
            "entryTitle": entry
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(entryPage),
            "entryTitle": entry
        })

def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={"entry": randomEntry}))

def search(request):
    value = request.GET.get('q','')
    for entry in util.list_entries():
        if value.upper() == entry.upper():
            value = entry;
    if (util.get_entry(value)) is not None:
        return HttpResponseRedirect(reverse("entry", kwargs={"entry": value}))
    else:
        subStringEntries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subStringEntries.append(entry)
        return render(request,"encyclopedia/index.html", {
            "entries": subStringEntries,
            "search": True,
            "value": value
        })
