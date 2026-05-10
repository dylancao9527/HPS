import click
from flask import current_app

from prediction.infrastructure.prophet_gateway import clear_prophet_model_cache
from prediction.infrastructure.prophet_model_store import LocalProphetModelStore
from prediction.infrastructure.repositories import PredictionRepository


def register_prophet_asset_commands(app):
    @app.cli.command("prophet-assets-cleanup")
    def prophet_assets_cleanup():
        repository = PredictionRepository()
        store = LocalProphetModelStore(current_app.config["PROPHET_MODEL_STORAGE_ROOT"])
        pruned_storage_keys = repository.prune_inactive_prophet_models(
            keep_inactive_per_slot=current_app.config["PROPHET_MAX_INACTIVE_METADATA_PER_SLOT"],
            max_inactive_age_hours=current_app.config["PROPHET_CLEANUP_MAX_INACTIVE_AGE_HOURS"],
        )
        removed_pruned = 0
        for storage_key in pruned_storage_keys:
            if store.exists(storage_key):
                store.delete_bundle(storage_key)
                removed_pruned += 1
        removed_legacy = 0
        for storage_key in store.list_legacy_storage_keys():
            store.delete_bundle(storage_key)
            removed_legacy += 1
        referenced = set(repository.list_prophet_storage_keys())
        removed_orphans = 0
        for storage_key in store.list_storage_keys():
            if storage_key not in referenced:
                store.delete_bundle(storage_key)
                removed_orphans += 1
        clear_prophet_model_cache()
        click.echo(
            f"removed_orphans={removed_orphans} removed_pruned={removed_pruned} removed_legacy={removed_legacy} pruned_inactive_rows={len(pruned_storage_keys)}"
        )
