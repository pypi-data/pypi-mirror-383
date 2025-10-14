import os
import pnp_ccv
from django.conf import settings
source_dir = os.path.dirname(pnp_ccv.__file__)
target_dir = os.path.join(settings.BASE_DIR, 'pnp_ccv')
if not os.path.exists(target_dir):
    os.symlink(source_dir, target_dir)