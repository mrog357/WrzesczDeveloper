from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from .forms import HexaProperties, NewPlotName, CsvModelForm
from users.models import Patrol
from .models import Plot, CashCode, Building, Neighborhood, Factors,Csvs
import csv
from django.urls import reverse
from django.utils import timezone


def check_admin(user):
   return user.is_superuser
def map(request):
    if request.user.is_authenticated:
        try:
            patrol = Patrol.objects.get(user=request.user)
        except Patrol.DoesNotExist:
            patrol = None
    else:
        patrol = None

    bg_image = Factors.objects.get(actual=True).map_background

    plot_list = Plot.objects.all()
    template = loader.get_template('map.html')
    context = {
        'plot_list': plot_list,
        'patrol': patrol,
        'bg_image': bg_image

    }


    return HttpResponse(template.render(context, request))

def zoom_map(request, zoom):
    plot_list = Plot.objects.all()

    plot_list_2 = []

    class plot_pos:
        def __init__(self, pos_x, pos_y, height, id, color, building):
            self.pic_position_x = pos_x
            self.pic_position_y = pos_y
            self.pic_height = height
            self.id = id
            self.color = color
            self.building = building

    if zoom > 0:
        zoom_factor = 1 + zoom * 0.5
        zoom_in = zoom + 1
        zoom_out = zoom - 1
    else:
        zoom_factor = 1
        zoom_in = zoom + 1
        zoom_out = zoom

    bg_width = 0
    bg_height = 0


    for plot in plot_list:
        to_add = plot_pos(int(plot.pic_position_x * zoom_factor),
                          int(plot.pic_position_y * zoom_factor),
                          int(plot.pic_height * zoom_factor),
                          plot.id,
                          plot.color,
                          plot.building
                          )
        plot_list_2.append(to_add)
        if to_add.pic_position_x > bg_width:
            bg_width = to_add.pic_position_x
        if to_add.pic_position_y > bg_height:
            bg_height = to_add.pic_position_y
    bg_width += (plot_list_2[0].pic_height + 6)
    bg_height += (plot_list_2[0].pic_height + 2)




    bg_image = Factors.objects.get(actual=True).map_background

    template = loader.get_template('zoom_map.html')
    context = {
        'plot_list': plot_list_2,
        'zoom_in': zoom_in,
        'zoom_out': zoom_out,
        'bg_image': bg_image,
        'bg_width': bg_width,
        'bg_height': bg_height
    }
    return HttpResponse(template.render(context, request))

@login_required
def add_code(request):
    patrol = get_object_or_404(Patrol, user=request.user)

    if request.GET.get("btn") and request.user.is_authenticated:
        requested_code = request.GET.get("inputed_code")

        try:
            cash_code = CashCode.objects.get(code_text=requested_code)
        except CashCode.DoesNotExist:
            messages.warning(request, f"Podano błędny kod")
        else:
            if cash_code.is_used:
                messages.warning(
                    request, f"Podany kod został wykorzystany"
                )
            else:
                patrol.cash += cash_code.cash_value
                cash_code.is_used = True
                patrol.save()
                cash_code.save()

                messages.success(request, f"Dodano {cash_code.cash_value}")

    return render(request, "add_code.html")

def plot(request, plot_id):
    if request.user.is_authenticated:
        try:
            patrol = Patrol.objects.get(user=request.user)
        except Patrol.DoesNotExist:
            patrol = None
    else:
        patrol = None

    try:
        plot = Plot.objects.get(pk=plot_id)

    except Plot.DoesNotExist:
        raise Http404("Plot does not exist")

    try:
        buildig_list = Building.objects.all().filter(available=True)

    except Building.DoesNotExist:
        raise Http404("Building does not exist")

    return render(request, 'plot.html', {'plot': plot, 'building_list': buildig_list, 'patrol': patrol})

def building(request, plot_id, building_name):
    if request.user.is_authenticated:
        try:
            patrol = Patrol.objects.get(user=request.user)
        except Patrol.DoesNotExist:
            patrol = None
    else:
        patrol = None

    try:
        plot = Plot.objects.get(pk=plot_id)

    except Plot.DoesNotExist:
        raise Http404("Plot does not exist")

    try:
        buildig = Building.objects.get(name=building_name)

    except Building.DoesNotExist:
        raise Http404("Building does not exist")

    return render(request, 'building.html', {'plot': plot, 'building': buildig, 'patrol': patrol})

@login_required
def build(request, plot_id, build_id):
    patrol = get_object_or_404(Patrol, user=request.user)

    try:
        plot = Plot.objects.get(pk=plot_id)
    except Plot.DoesNotExist:
        raise Http404("Plot does not exist")

    try:
        building = Building.objects.get(pk=build_id)
    except Building.DoesNotExist:
        raise Http404("Building does not exist")

    try:
        owner = plot.owner
    except:
        owner = None

    if owner:
        raise Http404("Plot is not available")
    else:
        if not building.available:
            messages.warning(request, f"Ten budynek jest niedostępny")
        else:
            if building.cost > patrol.cash:
                messages.warning(request, f"Nie masz wystarczająco pieniędzy.")

            else:
                remember_color = plot.color
                patrol.cash -= building.cost
                plot.building = building
                plot.owner = patrol
                plot.color = patrol.color
                if building.is_limited:
                    building.limit -= 1
                    if building.limit == 0:
                        building.available = False
                    building.save()
                plot.save()
                patrol.save()
                update_points(plot)
                # try:
                #     update_points(plot)
                # except:
                #     messages.warning(request, f"Problem z zakupem, skontaktuj się z administratrem")
                #     patrol.cash += building.cost
                #     plot.building = None
                #     plot.owner = None
                #     plot.color = remember_color
                #     plot.save()
                #     patrol.save()

    try:
        building_list = Building.objects.all()
    except Building.DoesNotExist:
        raise Http404("Plot is not available")

    return redirect('plot', plot_id)

def ranking(request):
    if request.user.is_authenticated:
        try:
            patrol = Patrol.objects.get(user=request.user)
        except Patrol.DoesNotExist:
            patrol = None
    else:
        patrol = None

    patrol_list = Patrol.objects.order_by('-points')
    template = loader.get_template('ranking.html')
    context = {
        'patrol_list': patrol_list,
        'patrol': patrol
    }
    return HttpResponse(template.render(context, request))
@user_passes_test(check_admin)
def adminex(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = HexaProperties(request.POST)
        # check whether it's valid:
        if form.is_valid():
            create_hexa_map(form.cleaned_data['vertical'], form.cleaned_data['horizontal'])
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HexaProperties()

        # if this is a POST request we need to process the form data




    return render(request, 'adminex.html', {'form': form})

@user_passes_test(check_admin)
def adminex_add_csv(request):
    try:
        obj = Csvs.objects.get(activated=False)
        with open(obj.file_name.path, 'r') as f:
            reader = csv.reader(f)

            for row in reader:
                row = "".join(row)
                row = row.replace(";", " ")
                row = row.split()
                CashCode.objects.create(
                    code_text=row[2],
                    cash_value=int(row[1]),
                    is_used=False)

        obj.activated = True
        obj.save()
    except:
        pass


    return redirect('adminex')

@user_passes_test(check_admin)
def adminex_map(request, zoom):
    plot_list = Plot.objects.all()

    plot_list_2 = []

    class plot_pos:
        def __init__(self, pos_x, pos_y, height, id, color, building):
            self.pic_position_x = pos_x
            self.pic_position_y = pos_y
            self.pic_height = height
            self.id = id
            self.color = color
            self.building = building

    if zoom > 0:
        zoom_factor = 1 + zoom * 0.5
        zoom_in = zoom + 1
        zoom_out = zoom - 1
    else:
        zoom_factor = 1
        zoom_in = zoom + 1
        zoom_out = zoom

    bg_width = 0
    bg_height = 0

    for plot in plot_list:
        to_add = plot_pos(int(plot.pic_position_x * zoom_factor),
                          int(plot.pic_position_y * zoom_factor),
                          int(plot.pic_height * zoom_factor),
                          plot.id,
                          plot.color.icon,
                          plot.color,
                          plot.building
                          )
        plot_list_2.append(to_add)
        if to_add.pic_position_x > bg_width:
            bg_width = to_add.pic_position_x
        if to_add.pic_position_y > bg_height:
            bg_height = to_add.pic_position_y
    bg_width += (plot_list_2[0].pic_height + 6)
    bg_height += (plot_list_2[0].pic_height + 2)

    bg_image = Factors.objects.get(actual=True).map_background

    template = loader.get_template('zoom_map.html')
    context = {
        'plot_list': plot_list_2,
        'zoom_in': zoom_in,
        'zoom_out': zoom_out,
        'bg_image': bg_image,
        'bg_width': bg_width,
        'bg_height': bg_height
    }
    return HttpResponse(template.render(context, request))

@user_passes_test(check_admin)
def adminex_plot(request, plot_id):

    if request.user.is_authenticated:
        try:
            patrol = Patrol.objects.get(user=request.user)
        except Patrol.DoesNotExist:
            patrol = None
    else:
        patrol = None

    try:
        plot = Plot.objects.get(pk=plot_id)

    except Plot.DoesNotExist:
        raise Http404("Plot does not exist")

    try:
        buildig_list = Building.objects.all()

    except Building.DoesNotExist:
        raise Http404("Building does not exist")
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewPlotName(request.POST)
        # check whether it's valid:
        if form.is_valid():
            plot.name = form.cleaned_data['new_name']
            plot.save()
            return render(request, 'adminex_plot.html', {'form': form, 'plot': plot, 'building_list': buildig_list, 'patrol': patrol})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewPlotName()

    return render(request, 'adminex_plot.html', {'form': form, 'plot': plot, 'building_list': buildig_list, 'patrol': patrol})

@user_passes_test(check_admin)
def adminex_build(request, plot_id, building_name):

    patrol = get_object_or_404(Patrol, user=request.user)

    try:
        plot = Plot.objects.get(pk=plot_id)
    except Plot.DoesNotExist:
        raise Http404("Plot does not exist")

    try:
        building = Building.objects.get(name=building_name)
    except Building.DoesNotExist:
        raise Http404("Building does not exist")

    remember_color = plot.color
    plot.building = building
    if building.color:
        plot.color = building.color
    else:
        plot.color = patrol.color
    plot.owner = patrol
    if not building.available:
        plot.name = building.name
    plot.save()
    patrol.save()
    try:
        update_points(plot)
    except:
        messages.warning(request, f"Problem z zakupem, skontaktuj się z administratrem")

        plot.building = None
        plot.owner = None
        plot.color = remember_color
        plot.save()
        patrol.save()

    try:
        building_list = Building.objects.all()
    except Building.DoesNotExist:
        raise Http404("Building does not exist")

    return redirect('adminex_plot', plot_id)

@user_passes_test(check_admin)
def adminex_update_all(request):

    plot_list = Plot.objects.all()
    for plot in plot_list:
        if plot.building:
            update_points(plot)


    return redirect('adminex')
def update_points(cause_plot):

    try:
        connection_bonus = Factors.objects.get(actual=True).connection_bonus
    except:
        connection_bonus = 0


    if cause_plot.building_bonus_exist():
        class PAP:
            def __init__(self, plot_id, proximity):
                self.proximity = proximity
                self.plot_id = plot_id

        to_visit = []
        visited = []

        neighborhood = Neighborhood.objects.get(base=cause_plot)
        for i in range(1, 6):
             pap = PAP(neighborhood.neighbor(i).id, 1)
             to_visit.append(pap)

        while to_visit:
            visiting_pap = to_visit.pop(0)
            open_plot = Plot.objects.get(id=visiting_pap.plot_id)
            open_plot.add_bonus(cause_plot.building_bonus(visiting_pap.proximity))
            open_plot.update_points()
            if(visiting_pap.proximity<6):
                neighborhood = Neighborhood.objects.get(base=cause_plot)
                for i in range(1, 6):
                    pap = PAP(neighborhood.neighbor(i), 1)
                    if to_visit.count(pap):
                        if visited.count(pap.plot_id):
                            to_visit.append(pap)
            visited.append(visiting_pap)




    neighborhood = Neighborhood.objects.get(base=cause_plot)
    for i in range (1,6):
        open_plot = neighborhood.neighbor(i)
        if open_plot.owner == cause_plot.owner:
            cause_plot.add_bonus(connection_bonus)
            open_plot.add_bonus(connection_bonus)
            open_plot.update_points()
            cause_plot.update_points()



def create_hexa_map(n, m):

    try:
       example = Plot.objects.get(name='Example')
    except:
        raise Http404("Example is not available")

    height = example.pic_height
    position_x = example.pic_position_x
    position_y = example.pic_position_y
    color = example.color

    plot_list = Plot.objects.all()
    for plot in plot_list:
        plot.delete()






    for i in range (0,m):
        for j in range(0,n):
            if i % 2:
                pos_x = position_x+j*2*height*0.9
            else:
                pos_x = position_x+(j*2+1)*height*0.9

            plot = Plot(
                        color=color,
                        name = ("Działka " + str(j+1)+ " w rzędzie " + str(i+1)),
                        pic_position_x=pos_x,
                        pic_position_y=int(position_y + i*height*0.55),
                        pic_height=height)
            plot.save()

            neighborhood = Neighborhood.objects.create(base=plot)

    plot_list = Plot.objects.order_by('id')
    k=0
    for plot in plot_list:

        print(str(plot.name))

        neighborhood= Neighborhood.objects.get(base=plot)
        try:
            neighborhood.neighbour_1 = Plot.objects.get(pk=(plot.id - 2*n))
        except:
            neighborhood.neighbour_1= None


        try:
            neighborhood.neighbour_2 = Plot.objects.get(pk=(plot.id - n))
        except:
            neighborhood.neighbour_2 = None

        try:
            neighborhood.neighbour_3 = Plot.objects.get(pk=(plot.id + 2 * n))
        except:
            neighborhood.neighbour_3 = None

        try:
            neighborhood.neighbour_4 = Plot.objects.get(pk=(plot.id + n))
        except:
            neighborhood.neighbour_4 = None

        if k > 2*n:
            k = 0
        if k < n:
            try:
                neighborhood.neighbour_5 = Plot.objects.get(pk=(plot.id - n + 1))
            except:
                neighborhood.neighbour_5 = None

            try:
                neighborhood.neighbour_6 = Plot.objects.get(pk=(plot.id + n + 1))
            except:
                neighborhood.neighbour_6 = None


        else:
            try:
                neighborhood.neighbour_5 = Plot.objects.get(pk=(plot.id - n - 1))
            except:
                neighborhood.neighbour_5 = None

            try:
                neighborhood.neighbour_6 = Plot.objects.get(pk=(plot.id + n - 1))
            except:
                neighborhood.neighbour_6 = None

        neighborhood.save()



