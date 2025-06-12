from django.shortcuts import render, get_object_or_404
from .models import Panel


def panel_detail(request, pk):
    panel = get_object_or_404(Panel.objects.prefetch_related('videos'), pk=pk)
    return render(request, 'panels/panel_detail.html', {'panel': panel})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PanelForm  # Panel formunu import ediyoruz

def panel_edit(request, id):
    panel = get_object_or_404(Panel, id=id)  # İlgili panel objesini al

    if request.method == 'POST':
        form = PanelForm(request.POST, instance=panel)
        if form.is_valid():
            form.save()
            return redirect('/panel/')  # Düzenledikten sonra liste sayfasına yönlendir
    else:
        form = PanelForm(instance=panel)  # Formu mevcut veriyle doldur

    context = {
        'form': form,
        'panel': panel,
    }
    return render(request, 'panels/edit.html', context)

def panel_create(request):
    if request.method == 'POST':
        form = PanelForm(request.POST)
        if form.is_valid():
            panel = form.save(commit=False)  # Önce kaydetme
            panel.user = request.user        # User'ı atıyoruz
            panel.save()                     # Sonra kaydet
            return redirect('panels:list')
    else:
        form = PanelForm()

    context = {
        'form': form
    }
    return render(request, 'panels/create.html', context)

def panel_list(request):
    panels = Panel.objects.all().order_by('-created_at')  # Oluşturulma tarihine göre sıralama (son eklenenler önde)
    context = {
        'panels': panels,
    }
    return render(request, 'panels/list.html', context)