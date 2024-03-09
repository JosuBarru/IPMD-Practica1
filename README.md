# Índice

1. [Descripción del problema](#descripción-del-problema)
2. [Parte 1 - Ejecución directa](#parte-1---ejecución-directa)
3. [Parte 2 - Aplicación en un contenedor](#parte-2---aplicación-en-un-contenedor)
4. [Parte 3 - Docker compose](#parte-3---docker-compose)
5. [Parte 4 - Kubernetes](#parte-4---kubernetes)

## Descripción del problema

El problema plantea la creación de un servicio web utilizando Flask en Python, que integre datos de las APIs de OpenData Euskadi y AEMET. El servicio web debe ofrecer tres endpoints:

1. **GET /test**: Devuelve un mensaje de "OK" si el servidor está operativo.
2. **GET /trafico/{autopista}**: Devuelve el último parte de incidencias de tráfico en la autopista seleccionada.
3. **GET /tiempo/{ciudad}**: Devuelve la última predicción de temperaturas máximas y mínimas para la ciudad seleccionada.

Se deben tener en cuenta consideraciones importantes como el uso de servidores recomendados para producción, manejo de claves de API, formato JSON en respuestas, entre otros.

## Parte 1 - Ejecución directa

En esta parte se realiza la implementación y pruebas del servicio web utilizando Flask. Se deben realizar todas las pruebas sin utilizar contenedores.

## Parte 2 - Aplicación en un contenedor

Construcción de una imagen de contenedor que permita la ejecución del servicio web. Se debe proporcionar un Dockerfile para la construcción de la imagen y luego ejecutar el contenedor utilizando el comando `docker run`.

## Parte 3 - Docker compose

Preparación de la aplicación para funcionar con Docker Compose. Se deben ofrecer los servicios `/test`, `/trafico` y `/tiempo` en contenedores separados, permitiendo su escalabilidad. Además, se debe incluir un balanceador de carga basado en un contenedor nginx.

## Parte 4 - Kubernetes

Implementación del servicio de API utilizando un clúster Kubernetes. Se debe proporcionar un documento .yaml unificado para la configuración. Se plantean dos versiones: servidores idénticos y servidores especializados. En ambos casos se debe considerar el uso de un balanceador de carga o un recurso ingress según sea necesario.

Se puede considerar una mejora adicional donde se incluya un servicio accesible a través de `/test` que compruebe que el resto de los servicios están en marcha con al menos una instancia.
https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/

### Implementación en servidor cloud

Para ejecutar la aplicación en un servidor cloud se ha usado Microsoft Azure. Para ello, tras crearnos la cuenta de estudiante, hemos creado un grupo de recursos y un clúster de Kubernetes. 

A continuación, para manejar de manera local el clúster de Kubernetes, hemos instalado la CLI de Azure, hemos hecho login con `az login`, establecido la suscripción del cluster con el comando `az account set --subscription <id> ` y nos descargamos las credenciales del clúster con el comando `az aks get-credentials --resource-group <nombre_grupo> --name <nombre_cluster>`, con esto modificamos el contexto de kubectl para que apunte al clúster de Azure, esto se encuentra en el archivo `~/.kube/config`.

Ahora, al ejecutar `kubectl get nodes` deberíamos ver los nodos del clúster de Azure. [comment]: <> (muestra un ejemplo de ejecución de kubectl get nodes)

```bash
$ kubectl get nodes
NAME                                STATUS   ROLES   AGE   VERSION
aks-agentpool-28800719-vmss000002   Ready    agent   19m   v1.27.9
aks-agentpool-28800719-vmss000003   Ready    agent   19m   v1.27.9
```

Podemos ver como el clúster de Azure tiene dos nodos. Ahora, para desplegar la aplicación definida en el archivo [serviciosIdenticos.yaml](./serviciosIdenticos.yaml)
en el clúster de Azure, tan solo tenemos que ejecutar el comando `kubectl apply -f serviciosIdenticos.yaml`.


Para probar que la aplicación se ha desplegado correctamente, podemos ejecutar el comando `kubectl get pods` para ver los pods que se han creado.
```bash
$ kubectl get pods
NAME                             READY   STATUS    RESTARTS   AGE
nginx-deployment-dc7d787-cxpnh   1/1     Running   0          16m
nginx-deployment-dc7d787-srq8f   1/1     Running   0          16m
nginx-deployment-dc7d787-wn29d   1/1     Running   0          16m
```

En este caso, al estar trabajando con un servicio cloud y tener un servicio del tipo NodePort, para acceder a la aplicación necesitamos saber la IP pública del nodo y el puerto que se ha asignado al servicio. Para ello, ejecutamos el comando `kubectl get services` y buscamos el servicio que nos interesa.

Para la versión de servicios especializados, se ha creado el archivo [serviciosEspecializados.yaml](./serviciosEspecializados.yaml) y se ha desplegado de la misma manera que el anterior.

En este caso, tenemos que tener en cuenta que el servicio de tipo Ingress necesita una IP pública para poder acceder a él. Para ello, ejecutamos el comando `kubectl get ingress` y buscamos el servicio que nos interesa.

```bash
$ kubectl get ingress
NAME            CLASS   HOSTS             ADDRESS   PORTS   AGE
nginx-ingress   nginx   aplicacion.com              80      12m
```

Como podemos ver no se le esta asignando ninguna dirección IP, para solucionar esto hay que recurrir a la [documentación de Azure](https://learn.microsoft.com/en-us/azure/aks/ingress-basic?tabs=azure-cli) y seguir los pasos para asignar una IP estática a nuestro servicio de Ingress.

```bash
NAMESPACE=ingress-basic

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace $NAMESPACE \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
  --set controller.service.externalTrafficPolicy=Local
```

Una vez hecho esto, podemos volver a ejecutar el comando `kubectl get ingress` y ver que se le ha asignado una dirección IP.

```bash
$ kubectl get ingress
NAME            CLASS   HOSTS             ADDRESS         PORTS   AGE
nginx-ingress   nginx   aplicacion.com   57.151.8.80     80      13m

