from site_setup.models import SiteSetup

def example(request):
    return {
        'example': 'Veio do context processor (example)'
    }

def site_setup(request):
    setup = SiteSetup.objects.order_by('-id').first()


    return {
        'site_setup': setup
    }
