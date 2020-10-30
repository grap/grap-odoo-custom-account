[1mdiff --git a/grap_account_export_ebp/migrations/12.0.1.0.1/post-migration.py b/grap_account_export_ebp/migrations/12.0.1.0.1/post-migration.py[m
[1mindex 5506bb9..8297a22 100644[m
[1m--- a/grap_account_export_ebp/migrations/12.0.1.0.1/post-migration.py[m
[1m+++ b/grap_account_export_ebp/migrations/12.0.1.0.1/post-migration.py[m
[36m@@ -2,7 +2,13 @@[m
 # @author: Sylvain LE GAL (https://twitter.com/legalsylvain)[m
 # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).[m
 [m
[31m-from openupgradelib import openupgrade, openupgrade_90[m
[32m+[m[32mimport logging[m
[32m+[m
[32m+[m[32mfrom openupgradelib import openupgrade[m
[32m+[m[32mfrom openupgradelib import openupgrade_90[m
[32m+[m
[32m+[m[32mlogger = logging.getLogger(__name__)[m
[32m+[m
 [m
 attachment_fields = {[m
     "ebp.export": [[m
[36m@@ -13,6 +19,7 @@[m [mattachment_fields = {[m
 }[m
 [m
 [m
[31m-@openupgrade.migrate(use_env=True)[m
[32m+[m[32m@openupgrade.migrate(no_version=True, use_env=True)[m
 def migrate(env, version):[m
[32m+[m[32m    logger.info("[grap_account_export_ebp] Converting fields to attachement")[m
     openupgrade_90.convert_binary_field_to_attachment(env, attachment_fields)[m
[1mdiff --git a/grap_account_export_ebp/migrations/12.0.1.0.1/pre-migration.py b/grap_account_export_ebp/migrations/12.0.1.0.1/pre-migration.py[m
[1mindex 422cc18..d9572a1 100644[m
[1m--- a/grap_account_export_ebp/migrations/12.0.1.0.1/pre-migration.py[m
[1m+++ b/grap_account_export_ebp/migrations/12.0.1.0.1/pre-migration.py[m
[36m@@ -2,8 +2,12 @@[m
 # @author: Sylvain LE GAL (https://twitter.com/legalsylvain)[m
 # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).[m
 [m
[32m+[m[32mimport logging[m
[32m+[m
 from openupgradelib import openupgrade[m
 [m
[32m+[m[32mlogger = logging.getLogger(__name__)[m
[32m+[m
 column_renames = {[m
     "ebp.export": [[m
         ("data_moves", None),[m
[36m@@ -13,6 +17,7 @@[m [mcolumn_renames = {[m
 }[m
 [m
 [m
[31m-@openupgrade.migrate()[m
[32m+[m[32m@openupgrade.migrate(no_version=True, use_env=True)[m
 def migrate(cr, version):[m
[32m+[m[32m    logger.info("[grap_account_export_ebp] Preserve data fields ...")[m
     openupgrade.rename_columns(cr, column_renames)[m
