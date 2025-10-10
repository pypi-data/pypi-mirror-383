"""
GODML Notebook API
-------------------

Una capa delgada y amigable para usar GODML desde notebooks.
Principios: síncrona, sin efectos colaterales inesperados y con retornos simples.

Funciones clave expuestas:
- DataPrep: `dataprep_preview`, `dataprep_run`, `dataprep_run_inline`
- Entrenamiento: `train_model`, `predict`, `evaluate`, `compare_models`
- Compliance: `apply_compliance`
- Utilidades: `save_artifact`, `load_artifact`, `emit_lineage`, `summarize_df`, `plot_roc_pr_curves`

Requiere que el proyecto GODML esté instalable/importable en el entorno del notebook.
"""
from __future__ import annotations

from joblib import dump, load
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
from godml.advisor_service.advisor_orchestrator import AdvisorOrchestrator
from godml.advisor_service.doc_rag_advisor import DocRAGAdvisor
from godml.advisor_service.metric_judge import MetricJudge
from godml.advisor_service.llm_advisor import LLMAdvisor

import pandas as pd
import numpy as np
import tempfile
import json
import yaml
import importlib

# -----------------------------
# DataPrep wrappers
# -----------------------------
try:
    from godml.dataprep_service.recipe_executor import (
        preview_recipe as _preview_recipe,
        run_recipe as _run_recipe,
        validate_recipe as _validate_recipe,
    )
except Exception as e:  # pragma: no cover
    raise ImportError(
        "No se pudo importar godml.dataprep_service. ¿Está GODML instalado en este entorno?"
    ) from e


def dataprep_preview(
    recipe_path: str | Path,
    limit: int = 20,
    governance: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Ejecuta la receta en modo *preview* y devuelve el `head(limit)` final.

    Parameters
    ----------
    recipe_path : str | Path
        Ruta al YAML de receta.
    limit : int
        Número de filas a mostrar/retornar.
    governance : dict | None
        Parámetros de gobernanza (p. ej., {"compliance": "pci-dss"}).
    """
    recipe_path = Path(recipe_path)
    _validate_recipe(recipe_path)
    return _preview_recipe(recipe_path, limit=limit, governance=governance)


def dataprep_run(
    recipe_path: str | Path,
    governance: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Ejecuta la receta completa (READ → TRANSFORMS → COMPLIANCE → VALIDATIONS → WRITE)
    y devuelve el `DataFrame` final en memoria.
    """
    recipe_path = Path(recipe_path)
    _validate_recipe(recipe_path)
    return _run_recipe(recipe_path, mode="run", governance=governance)


def dataprep_run_inline(
    recipe: Dict[str, Any] | Any,
    governance: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Permite pasar la receta como dict o como objeto Pydantic Recipe."""
    # ✅ Normaliza a dict si viene como Pydantic (v2 o v1)
    if hasattr(recipe, "model_dump"):
        recipe = recipe.model_dump()
    elif hasattr(recipe, "dict"):
        recipe = recipe.dict()

    payload = {"dataprep": recipe} if isinstance(recipe, dict) and "inputs" in recipe else recipe

    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=False)
        tmp = Path(f.name)
    return _run_recipe(tmp, mode="run", governance=governance)


# -----------------------------
# Model training & evaluation
# -----------------------------

# Model registry mínimo (extensible)
_DEF_REGISTRY: Dict[str, str] = {
    "random_forest": "godml.model_service.model_registry.random_forest_model:RandomForestModel",
    "rf": "godml.model_service.model_registry.random_forest_model:RandomForestModel",
    "xgboost": "godml.model_service.model_registry.xgboost_model:XgboostModel",
    "xgb": "godml.model_service.model_registry.xgboost_model:XgboostModel",
}


def _import_symbol(path: str) -> Any:

    module_path, _, attr = path.partition(":")
    mod = importlib.import_module(module_path)
    return getattr(mod, attr)


def _fit_any(m, X, y, hyperparams: Dict[str, Any] | None = None):
    """
    Intenta entrenar con múltiples convenciones de wrapper:
    - m.fit(X, y)
    - m.train(X, y)
    - m.train(X, y, params)
    - m.train(X, y, X_test, y_test)
    - m.train(X, y, X_test, y_test, params)
    - m.estimator.fit(...), m.clf.fit(...), m.model.fit(...)
    - o cualquier subatributo con método fit(...)
    """
    hyperparams = hyperparams or {}

    # candidatos directos y comunes
    candidates = [
        m,
        getattr(m, "estimator", None),
        getattr(m, "clf", None),
        getattr(m, "model", None),
    ]
    for cand in candidates:
        if cand is None:
            continue

        # 1) fit(X, y)
        fit = getattr(cand, "fit", None)
        if callable(fit):
            try:
                fit(X, y)
                return
            except TypeError:
                # si la firma no encaja, probamos train(...)
                pass

        # 2) train(...) con firmas alternativas — OJO: no llamar train(X,y) directo
        train = getattr(cand, "train", None)
        if callable(train):
            trials = [
                (X, y),
                (X, y, {}),                         # algunos wrappers piden params
                (X, y, None),
                (X, y, X, y),                       # train(X_tr, y_tr, X_te, y_te)
                (X, y, X, y, {}),                   # + params vacío
                (X, y, X, y, hyperparams or {}),    # + hyperparams si vienen
            ]
            for args in trials:
                try:
                    train(*args)
                    return
                except TypeError:
                    continue
            # si ninguna firma funcionó, pasamos al siguiente candidato

    # 3) Último recurso: buscar sub-atributos con .fit(X,y)
    try:
        for v in vars(m).values():
            fit = getattr(v, "fit", None)
            if callable(fit):
                try:
                    fit(X, y)
                    return
                except TypeError:
                    continue
    except Exception:
        pass

    raise AttributeError("El modelo no expone 'fit', 'train' ni sub-atributos compatibles para entrenamiento")


def _predict_any(m, X):
    """
    Predicción tolerante a wrappers:
    - usa predict_proba si existe; si no, predict
    - busca en .estimator/.clf/.model o cualquier atributo con predict(_proba)
    """
    def _try_one(obj):
        if obj is None:
            return None
        if hasattr(obj, "predict_proba"):
            try:
                import numpy as np
                proba = obj.predict_proba(X)
                if isinstance(proba, (list, tuple)):
                    proba = proba[1]
                return proba[:, 1] if hasattr(proba, "ndim") and proba.ndim == 2 and proba.shape[1] > 1 else proba
            except Exception:
                pass
        if hasattr(obj, "predict"):
            return obj.predict(X)
        return None

    # orden de prueba
    for cand in [m, getattr(m, "model", None), getattr(m, "estimator", None), getattr(m, "clf", None)]:
        out = _try_one(cand)
        if out is not None:
            return out

    # último recurso: scan atributos
    try:
        for v in vars(m).values():
            out = _try_one(v)
            if out is not None:
                return out
    except Exception:
        pass
    raise AttributeError("No se encontró método de predicción compatible en el modelo/wrapper")


def _get_model(model_type: str, **hyperparams):
    key = (model_type or "").lower()
    if key not in _DEF_REGISTRY:
        raise ValueError(
            f"Modelo no soportado: {model_type}. Disponibles: {sorted(set(_DEF_REGISTRY))}"
        )
    cls = _import_symbol(_DEF_REGISTRY[key])
    # 1) intenta kwargs; 2) si falla, instancia vacío y aplica params
    try:
        return cls(**(hyperparams or {}))
    except TypeError:
        model = cls()
        if hyperparams:
            if hasattr(model, "set_params") and callable(getattr(model, "set_params")):
                try:
                    model.set_params(**hyperparams)
                    return model
                except Exception:
                    pass
            # fallback fino-graneado
            for k, v in hyperparams.items():
                try:
                    setattr(model, k, v)
                except Exception:
                    pass
        return model


def train_model(
    model_type: str,
    X: pd.DataFrame,
    y: pd.Series,
    hyperparams: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = None,
):
    """Entrena un modelo soportado y devuelve un contenedor ligero con `.model`."""

    # _get_model ya manejará si puede o no pasar los hyperparams al __init__
    model = _get_model(model_type, **(hyperparams or {}))

    # Si el modelo soporta set_random_state
    if seed is not None and hasattr(model, "set_random_state"):
        try:
            model.set_random_state(seed)
        except Exception:
            pass

    # Si el wrapper tiene un setter específico de hiperparámetros
    if hyperparams and hasattr(model, "set_hyperparameters"):
        try:
            model.set_hyperparameters(hyperparams)
        except Exception:
            pass

    # Entrenamiento tolerante a wrappers (pasamos hyperparams por si el wrapper los requiere en train)
    _fit_any(model, X, y, hyperparams or {})

    return type("ModelResultLike", (), {"model": model, "metrics": None})()



def predict(model_or_wrapper: Any, X: pd.DataFrame):
    """Predice usando un estimador o wrapper, con fallbacks para .model/.estimator/.clf."""
    model = getattr(model_or_wrapper, "model", model_or_wrapper)
    return _predict_any(model, X)


def evaluate(y_true, y_pred, metrics: Sequence[str] | Dict[str, Any]) -> Dict[str, float]:
    """Calcula métricas. Si existe `monitoring_service.metrics.compute_metrics`, lo usa.
    En caso contrario, calcula un subconjunto con scikit-learn si está disponible.
    """
    # Intento 1: usar orquestador del proyecto
    try:  # pragma: no cover
        from godml.monitoring_service.metrics import compute_metrics as _cm

        return _cm(y_true, y_pred, metrics)
    except Exception:
        pass

    # Fallback: sklearn básico
    try:
        from sklearn import metrics as sk
    except Exception as e:  # pragma: no cover
        raise ImportError(
            "No se encontró compute_metrics y tampoco sklearn; instala scikit-learn o expón monitoring_service.metrics.compute_metrics"
        ) from e

    wanted = list(metrics.keys()) if isinstance(metrics, dict) else list(metrics)
    out: Dict[str, float] = {}
    # Heurística: si y_pred es probabilidades y contiene valores entre 0 y 1

    y_pred_arr = np.asarray(y_pred)
    is_prob_like = y_pred_arr.dtype.kind in {"f"} and y_pred_arr.min() >= 0 and y_pred_arr.max() <= 1

    for m in wanted:
        m_l = m.lower()
        if m_l in {"accuracy", "acc"}:
            out[m] = float(sk.accuracy_score(y_true, (y_pred_arr > 0.5) if is_prob_like else y_pred_arr))
        elif m_l in {"precision", "prec"}:
            out[m] = float(sk.precision_score(y_true, (y_pred_arr > 0.5) if is_prob_like else y_pred_arr))
        elif m_l in {"recall", "tpr"}:
            out[m] = float(sk.recall_score(y_true, (y_pred_arr > 0.5) if is_prob_like else y_pred_arr))
        elif m_l in {"f1", "f1_score"}:
            out[m] = float(sk.f1_score(y_true, (y_pred_arr > 0.5) if is_prob_like else y_pred_arr))
        elif m_l in {"roc_auc", "auc"} and is_prob_like:
            out[m] = float(sk.roc_auc_score(y_true, y_pred_arr))
        else:
            # Intento genérico si sklearn tiene la métrica
            func = getattr(sk, f"{m_l}_score", None)
            if callable(func):
                out[m] = float(func(y_true, y_pred_arr))
    return out


def compare_models(results: Iterable[Any], by: str = "roc_auc") -> pd.DataFrame:
    """Construye una tabla comparativa a partir de resultados (cada uno con `.metrics`)."""
    rows = []
    for r in results:
        metrics = getattr(r, "metrics", None) or {}
        rows.append({"model": type(getattr(r, "model", r)).__name__, **metrics})
    df = pd.DataFrame(rows)
    if by in df.columns:
        df = df.sort_values(by=by, ascending=False)
    return df.reset_index(drop=True)


# -----------------------------
# Compliance helpers
# -----------------------------

def apply_compliance(df: pd.DataFrame, standard: str = "pci-dss") -> pd.DataFrame:
    """Aplica reglas de cumplimiento (hoy: PCI-DSS) sobre un DataFrame."""
    std = (standard or "").lower().strip()
    if std != "pci-dss":
        return df
    from godml.compliance_service.pci_dss import PciDssCompliance

    return PciDssCompliance().apply(df.copy())


# -----------------------------
# Artifacts, lineage & utils
# -----------------------------

def save_artifact(obj: Any, path: str | Path) -> None:
    """Guarda un objeto (modelo, grid, resultados) mediante joblib."""

    dump(obj, Path(path))


def load_artifact(path: str | Path) -> Any:

    return load(Path(path))


def emit_lineage(event_type: str, payload: Dict[str, Any]) -> None:
    """Emite un evento de lineage con el stub OpenLineage incluido en GODML."""
    try:
        from godml.dataprep_service.lineage.openlineage_emitter import emit

        emit(event_type, payload)
    except Exception:  # pragma: no cover
        pass


def summarize_df(df: pd.DataFrame) -> Dict[str, Any]:
    """Resumen rápido: filas, columnas, nulos y cardinalidad por columna."""
    summary = {
        "shape": list(df.shape),
        "nulls": df.isna().sum().to_dict(),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "unique": {c: int(df[c].nunique(dropna=True)) for c in df.columns},
    }
    return summary


def plot_roc_pr_curves(y_true, y_prob) -> None:
    """Dibuja ROC y PR en dos figuras separadas (reglas: una figura por gráfico, sin estilos)."""
    try:
        from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score
    except Exception as e:  # pragma: no cover
        raise ImportError("Se requiere scikit-learn para graficar curvas ROC/PR.") from e

    import matplotlib.pyplot as plt

    # ROC
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, label=f"ROC AUC = {roc_auc:.3f}")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.show()

    # PR
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    ap = average_precision_score(y_true, y_prob)
    plt.figure()
    plt.plot(recall, precision, label=f"AP = {ap:.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend(loc="lower left")
    plt.show()

# =========================
# AutoTuning (MVP sklearn)
# =========================

def suggest_search_space(model_type: str) -> dict:
    """
    Espacios de búsqueda recomendados por modelo.
    Pensados para RandomizedSearchCV (listas discretas).
    """
    m = (model_type or "").lower()
    if m in {"random_forest", "rf"}:
        return {
            "n_estimators": [100, 200, 400, 800],
            "max_depth": [3, 4, 6, 8, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2", None],
            "bootstrap": [True, False],
        }
    if m in {"xgboost", "xgb"}:
        # API sklearn de XGBoost (XGBClassifier)
        return {
            "n_estimators": [100, 200, 400, 800],
            "max_depth": [3, 4, 6, 8],
            "learning_rate": [0.03, 0.05, 0.1, 0.2],
            "subsample": [0.7, 0.8, 1.0],
            "colsample_bytree": [0.7, 0.8, 1.0],
            "reg_lambda": [0.0, 1.0, 3.0, 5.0],
        }
    if m in {"logistic_regression", "logreg", "logistic"}:
        return {
            "C": [0.01, 0.1, 1.0, 3.0, 10.0],
            "penalty": ["l2"],
            "solver": ["lbfgs"],
            "max_iter": [200, 400, 800],
        }
    return {}


def _sklearn_scoring(metric: str, y) -> str:
    """
    Mapa de métricas a 'scoring' de sklearn.
    Soporta multiclase básico para roc_auc.
    """
    m = (metric or "").lower().strip()
    if m == "roc_auc":
        return "roc_auc_ovr" if getattr(y, "nunique", lambda: 2)() > 2 else "roc_auc"
    return m  # accuracy, f1, precision, recall, r2, etc.


def tune_model(
    model_type: str,
    X,
    y,
    search_space: dict | None = None,
    metric: str = "roc_auc",
    cv: int = 5,
    max_trials: int = 30,
    time_budget_s: int | None = None,  # reservado para Optuna en fase 2
    seed: int = 42,
    use_optuna: bool = False,
    n_jobs: int | None = None,
):
    """
    AutoTuning con RandomizedSearchCV (por defecto).
    Retorna:
        {
          "best_params": dict,
          "best_score": float,
          "cv_results": pd.DataFrame,
          "best_estimator": fitted_estimator
        }
    """
    # Intento Optuna (fase 2)
    if use_optuna:
        try:
            import optuna  # noqa: F401
        except Exception:
            print("⚠️ Optuna no está instalado; continuo con RandomizedSearchCV.")
            use_optuna = False

    if use_optuna:
        raise NotImplementedError("Optuna backend no implementado aún.")

    # --- sklearn backend ---
    try:
        from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, KFold
        import pandas as _pd
    except Exception as e:  # pragma: no cover
        raise ImportError("Se requiere scikit-learn para tune_model().") from e

    # Resolver estimator sklearn-friendly según el tipo
    EstCls = _sk_estimator_for(model_type)
    try:
        tmp = EstCls()
        est_params = tmp.get_params()
    except Exception:
        est_params = {}
    est_kwargs = {}
    if "random_state" in est_params:
        est_kwargs["random_state"] = seed
    estimator = EstCls(**est_kwargs)

    # Espacio por defecto si no te pasaron uno
    search_space = search_space or suggest_search_space(model_type)

    # CV estratificado si parece clasificación (<=20 clases)
    is_classif = getattr(y, "nunique", lambda: 2)() <= 20
    cv_split = StratifiedKFold(n_splits=cv, shuffle=True, random_state=seed) if is_classif else KFold(n_splits=cv, shuffle=True, random_state=seed)
    scoring = _sklearn_scoring(metric, y)

    rs = RandomizedSearchCV(
        estimator=estimator,
        param_distributions=search_space,
        n_iter=max_trials,
        scoring=scoring,
        cv=cv_split,
        random_state=seed,
        n_jobs=n_jobs if n_jobs is not None else (-1 if is_classif else None),
        verbose=0,
        refit=True,  # entrena con best_params en todo el set
    )
    rs.fit(X, y)

    cv_df = _pd.DataFrame(rs.cv_results_)
    return {
        "best_params": rs.best_params_,
        "best_score": float(rs.best_score_),
        "cv_results": cv_df,
        "best_estimator": rs.best_estimator_,
    }


def _sk_estimator_for(model_type: str):
    """Devuelve la clase de estimator sklearn para el model_type."""
    key = (model_type or "").lower()
    if key in {"random_forest", "rf"}:
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier
    if key in {"logistic_regression", "logreg", "logistic"}:
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression
    if key in {"xgboost", "xgb"}:
        try:
            from xgboost import XGBClassifier  # requiere xgboost instalado
            return XGBClassifier
        except Exception as e:
            raise ImportError("xgboost no está instalado para usar XGBClassifier") from e
    raise ValueError(f"No hay mapeo sklearn para model_type='{model_type}'")

def optimize_threshold(y_true, y_prob, metric: str = "f1"):
    """
    Busca el mejor umbral en [0,1] para maximizar la métrica dada (f1, precision, recall).
    Retorna (best_threshold, best_score).
    """
    try:
        from sklearn import metrics as sk
        import numpy as np
    except Exception as e:  # pragma: no cover
        raise ImportError("Se requiere scikit-learn y numpy para optimize_threshold.") from e

    y_prob = np.asarray(y_prob).ravel()
    candidates = np.linspace(0.05, 0.95, 19)
    best_thr, best_score = 0.5, -1.0
    for thr in candidates:
        y_hat = (y_prob >= thr).astype(int)
        if metric == "f1":
            s = sk.f1_score(y_true, y_hat)
        elif metric == "precision":
            s = sk.precision_score(y_true, y_hat)
        elif metric == "recall":
            s = sk.recall_score(y_true, y_hat)
        else:
            # fallback: usa f1
            s = sk.f1_score(y_true, y_hat)
        if s > best_score:
            best_thr, best_score = thr, s
    return best_thr, float(best_score)

# ---------------------------------------------
# Integración con pipelines YAML y ejecutores
# (bloque solicitado por Arturo – compatibilidad con notebooks)
# ---------------------------------------------
from godml.core_service.parser import load_pipeline
from godml.core_service.executors import get_executor
from godml.config_service.schema import PipelineDefinition
from .utils.model_storage import save_model_to_structure, load_model_from_structure
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GodmlNotebook:
    def __init__(self):
        self.pipeline = None
        self.last_trained_model = None

    def create_pipeline(
        self,
        name: str,
        model_type: str,
        hyperparameters: dict,
        dataset_path: str,
        output_path: str | None = None,
    ):
        """Crea un PipelineDefinition en memoria listo para ejecutar desde notebook."""
        config = {
            "name": name,
            "version": "1.0.0",
            "provider": "mlflow",
            "dataset": {"uri": dataset_path, "hash": "auto"},
            "model": {"type": model_type, "hyperparameters": hyperparameters},
            "metrics": [{"name": "auc", "threshold": 0.8}],
            "governance": {
                "owner": "notebook-user@company.com",
                "tags": [{"source": "jupyter"}],
            },
            "deploy": {
                "realtime": False,
                "batch_output": output_path or f"./outputs/{name}_predictions.csv",
            },
        }
        self.pipeline = PipelineDefinition(**config)
        return self.pipeline

    def train(self):
        if not self.pipeline:
            raise ValueError("Primero crea un pipeline")
        executor = get_executor(self.pipeline.provider)
        result = executor.run(self.pipeline)
        # Guarda el último modelo entrenado para reutilizarlo
        try:
            self.last_trained_model = getattr(result, "model", None)
        except Exception:
            self.last_trained_model = None
        return "✅ Entrenamiento completado"

    def save_model(self, model=None, model_name: str | None = None, environment: str = "experiments"):
        """Guardar modelo en estructura organizada (utils.model_storage)."""
        model_to_save = model or self.last_trained_model
        if model_to_save is None:
            raise ValueError("No hay modelo para guardar. Entrena un modelo primero o proporciona uno.")
        return save_model_to_structure(model_to_save, model_name, environment)

    def load_model(self, model_name: str, environment: str = "production"):
        """Cargar modelo desde estructura (utils.model_storage)."""
        return load_model_from_structure(model_name, environment)


def quick_train(model_type: str, hyperparameters: dict, dataset_path: str, name: str | None = None):
    """Entrenamiento rápido sin fricción desde notebook."""
    godml = GodmlNotebook()
    name = name or f"{model_type}-quick-train"
    godml.create_pipeline(
        name=name,
        model_type=model_type,
        hyperparameters=hyperparameters,
        dataset_path=dataset_path,
    )
    godml.train()
    return "✅ Modelo entrenado exitosamente"

def quick_train_with_metrics(model_type: str, hyperparameters: dict, dataset_path: str, name: str | None = None):
    """Como quick_train, pero retorna un dict con métricas si el executor las expone."""
    godml = GodmlNotebook()
    name = name or f"{model_type}-quick-train"
    pipe = godml.create_pipeline(
        name=name,
        model_type=model_type,
        hyperparameters=hyperparameters,
        dataset_path=dataset_path,
    )
    executor = get_executor(pipe.provider)
    result = executor.run(pipe)  # suele tener .metrics y .model
    return {
        "message": f"✅ Modelo {model_type} entrenado",
        "metrics": getattr(result, "metrics", {}),
        "model": getattr(result, "model", None),
        "pipeline": pipe,
    }



# ---- Helpers para entrenar desde YAML ----

def train_from_yaml(yaml_path: str = "./godml/godml.yml"):
    """Entrenar usando configuración YAML existente."""
    try:
        pipeline = load_pipeline(yaml_path)
        executor = get_executor(pipeline.provider)
        executor.run(pipeline)
        return f"✅ Modelo {pipeline.model.type} entrenado desde {yaml_path}"
    except Exception as e:  # pragma: no cover
        return f"❌ Error: {e}"


def quick_train_yaml(model_type: str, hyperparameters: dict, yaml_path: str = "./godml/godml.yml"):
    """Entrenar modificando el YAML existente (cambia modelo e hiperparámetros al vuelo)."""
    try:
        pipeline = load_pipeline(yaml_path)
        print(f"🔄 Cambiando modelo de '{pipeline.model.type}' a '{model_type}'")
        try:
            print(f"🔧 Hiperparámetros originales: {pipeline.model.hyperparameters.model_dump()}")
        except Exception:
            try:
                print(f"🔧 Hiperparámetros originales: {pipeline.model.hyperparameters.dict()}")
            except Exception:
                pass
        # Actualiza tipo y params
        pipeline.model.type = model_type
        # Reinstancia los hyperparams con la misma clase si es posible
        try:
            hp_cls = type(pipeline.model.hyperparameters)
            pipeline.model.hyperparameters = hp_cls(**hyperparameters)
        except Exception:
            pipeline.model.hyperparameters = hyperparameters  # fallback
        pipeline.name = f"{pipeline.name}-{model_type}"
        print(f"🔧 Nuevos hiperparámetros: {hyperparameters}")
        executor = get_executor(pipeline.provider)
        executor.run(pipeline)
        return f"✅ Modelo {model_type} entrenado con configuración de {yaml_path}"
    except Exception as e:  # pragma: no cover
        return f"❌ Error: {e}"

def advisor(df, target: str = None):
    """Versión simple (sin RAG)"""
    orchestrator = AdvisorOrchestrator(use_rag=False)
    return orchestrator.analyze(df, target)

def advisor_rag(df, target: str = None, derive_target: bool = False):
    """Versión robusta con RAG de recetas"""
    orchestrator = AdvisorOrchestrator(use_rag=True)
    return orchestrator.analyze(df, target, derive_target)

def doc_advisor(question: str):
    """Asistente de documentación GODML con RAG"""
    bot = DocRAGAdvisor()
    return bot.ask(question)

def metric_judge(X, y, task_type="classification"):
    """
    Evalúa qué métricas son más adecuadas para un dataset específico.
    Usa MetricJudge internamente.
    """
    judge = MetricJudge()
    return judge.suggest(X, y, task_type=task_type)


def advisor_full_report(df, target: str = None, derive_target: bool = False):
    """
    Orquesta:
        - MetricJudge → métricas recomendadas
        - ModelSelector → modelos sugeridos
        - HyperparamAdvisor → espacio de hiperparámetros
        - DataQualityJudge → calidad de datos
        - LLMAdvisor / RAG → receta DataPrep
    Muestra el reporte completo en el notebook con formato bonito.
    """
    orch = AdvisorOrchestrator()
    report = orch.analyze(df, target=target, derive_target=derive_target)

    print("\n======================")
    print("📊 GODML FULL REPORT")
    print("======================")

    # 1) Métricas
    metrics = report.get("metrics", {})
    print("\n=== Métricas ===")
    print(f"🔎 Tipo de tarea: {metrics.get('task_type', 'N/A')}")
    if "metrics" in metrics:
        print("📌 Métricas recomendadas:", ", ".join(metrics["metrics"]))
    if "recipe" in metrics:
        print("📜 Receta mínima de DataPrep:")
        print(json.dumps(metrics["recipe"], indent=2, ensure_ascii=False))

    # 2) Modelos
    print("\n=== Modelos sugeridos ===")
    for i, model in enumerate(report.get("models", []), 1):
        print(f"⚡ {i}. {model}")

    # 3) Hyperparams
    print("\n=== Espacio de hiperparámetros ===")
    hyperparams = report.get("hyperparams", {})
    if hyperparams:
        for k, v in hyperparams.items():
            print(f"  - {k}: {v}")
    else:
        print("  (ninguno sugerido)")

    # 4) Calidad de datos
    print("\n=== Calidad de datos ===")
    quality = report.get("quality", {})
    for k, v in quality.items():
        print(f"  - {k}: {v}")

    # 5) Receta LLM
    print("\n=== Receta LLM (JSON para notebook) ===")
    recipe_llm = report.get("recipe_llm", None)
    if recipe_llm:
        print(json.dumps(recipe_llm, indent=2, ensure_ascii=False))
    else:
        print("  (no generada)")

    print("\n✅ Reporte completo generado.\n")

    return report