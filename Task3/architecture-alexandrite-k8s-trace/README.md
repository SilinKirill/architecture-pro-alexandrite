# Jaeger в Minikube с сервисами

## Описание

Развертывание Jaeger в Minikube с двумя сервисами, которые:

1. Взаимодействуют между собой.
2. Отправляют трейсы в Jaeger.

## Требования

- Minikube
- kubectl
- Docker

## Установка

### 1. Запуск Minikube

```bash
minikube start --addons=ingress
```

### 2. Установка cert-manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
```

### 3. Развертывание Jaeger

```bash
kubectl create namespace observability

kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability

kubectl set image deployment/jaeger-operator \
  kube-rbac-proxy=registry.k8s.io/kubebuilder/kube-rbac-proxy:v0.13.1 \
  -n observability

kubectl apply -f k8s/jaeger-instance.yaml
```

Проверка состояния Jaeger Operator:

```bash
kubectl get pods -n observability
```

Проверка состояния Jaeger:

```bash
kubectl get pods
```

### 4. Сборка и деплой сервисов

```bash
# Сборка образов
minikube image build -t service-a:latest services/service-a/
minikube image build -t service-b:latest services/service-b/

# Развертывание
kubectl apply -f k8s/services.yaml
```

Проверка:

```bash
kubectl get pods
```

## Проверка работы

### Тестирование сервисов

Получить имя pod service-a:

```bash
POD=$(kubectl get pods -l app=service-a -o jsonpath='{.items[0].metadata.name}')
```

Выполнить запрос к service-a:

```bash
kubectl exec -it "$POD" -- python -c \
'import requests; print(requests.get("http://service-a:8080/").text)'
```

`service-a` вызывает `service-b`, при этом оба вызова должны попасть в один trace.

При необходимости можно проверить логи:

```bash
kubectl logs -l app=service-a
kubectl logs -l app=service-b
```

### Доступ к Jaeger UI

```bash
kubectl port-forward svc/simplest-query 16686:16686
```

Открыть в браузере:

`http://localhost:16686`

В Jaeger выбрать `service-a`, нажать `Find Traces` и открыть последний trace.

В одном trace должны присутствовать `service-a` и `service-b`.

## Структура проекта

- `services/service-a/` — исходный код service-a
- `services/service-b/` — исходный код service-b
- `k8s/services.yaml` — конфигурация Kubernetes для сервисов
- `k8s/jaeger-instance.yaml` — конфигурация Jaeger
