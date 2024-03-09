# Trabajo práctico 1

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

Implementar el servicio de API utilizando un clúster kubernetes se ha considerado utilizar Minikube para la ejecución local. 

Se han implementado dos versiones del servicio, en ambas se trabaja con una imagen personalizada y que no esta descargada localmente en el clúster de minikube, por lo que se ha tenido que subir la imagen a Docker Hub para poder de alguna forma acceder a ella desde el clúster. 

Para el manejo de información sensible, como las claves de las APIs, se ha utilizado secrets de kubernetes, para ello se ha creado un archivo [secrets.yaml](./secrets.yaml) que define los secretos necesarios para el servicio web, que será más tarde montado en una variable de entorno en el deployment del servicio web. Para crear los secretos, se ha ejecutado el comando `kubectl apply -f secrets.yaml`.

### Servicios idénticos
Para esta primera versión se pedía desplegar n instancias del servicio web, cada una con un endpoint diferente, y un balanceador de carga que distribuyera las peticiones entre los tres servicios. Para ello, se ha creado el archivo [serviciosIdenticos.yaml](./serviciosIdenticos.yaml) que define un deployment con tres pods del servicio web y un servicio de tipo LoadBalancer que actúa como balanceador de carga entre los nodos (aunque en este caso solo hay uno) y los tres pods. Se crea el cluster con el comando `minikube start` y se realiza el despliegue con el comando `kubectl apply -f serviciosIdenticos.yaml`. 

Un servicio LoadBalancer no expone el servicio a través de una dirección IP, sino que delega en el proveedor de la nube para que asigne una dirección IP. En el caso de minikube, que es un clúster local, no se asigna una dirección IP, por lo que no se puede acceder al servicio desde el exterior. Para solucionar esto, es necesario crear un tunel con el comando `minikube tunnel`, que asigna una dirección IP a los servicios de tipo LoadBalancer.


```bash
minikube tunnel
Status:	
	machine: minikube
	pid: 63636
	route: 10.96.0.0/12 -> 192.168.49.2
	minikube: Running
	services: [nginx-service]
    errors: 
		minikube: no errors
		router: no errors
		loadbalancer emulator: no errors
```

Ahora, al ejecutar el comando `kubectl get services` deberíamos ver la IP pública asignada al servicio.

```bash
NAME            TYPE           CLUSTER-IP     EXTERNAL-IP    PORT(S)        AGE
kubernetes      ClusterIP      10.96.0.1      <none>         443/TCP        13m
nginx-service   LoadBalancer   10.96.82.214   10.96.82.214   80:30330/TCP   5m9s
```

Y se puede acceder localmente a la aplicación mediante la IP pública que se nos ha asignado.

```bash
curl 10.96.82.214/test
{"status":"OK"}
``` 

### Servicios especializados
Para esta segunda versión se pedía desplegar 1 instancia de /test, n instancias de /trafico y m instancias de /tiempo. Para ello, se ha creado el archivo [serviciosEspecializados.yaml](./serviciosEspecializados.yaml) que define un deployment con un pod del servicio web para /test, un deployment con 3 pods del servicio web para /trafico y un deployment con 4 pods del servicio web para /tiempo, cada uno de estos deployments con su correspondiente servicio de tipo ClusterIP para poder acceder a ellos desde el exterior. Además, se ha creado un servicio de tipo Ingress que actúa como balanceador de carga entre los tres servicios, teniendo en cuenta la URL de la petición para redirigirla al pod correspondiente.

Un ingress requiere que en el clúster esté instalado un controlador de ingreso. Por ejemplo, en minikube, el comando `minikube addons enable ingress` activa un controlador de ingreso basado en Nginx, ver https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/

Para realizar el despliegue, se ha ejecutado el comando `kubectl apply -f serviciosEspecializados.yaml`.

Ahora, al ejecutar el comando `kubectl get ingress` deberíamos ver la dirección IP asignada al servicio.

```bash
$ kubectl get ingress
NAME            CLASS   HOSTS             ADDRESS         PORTS   AGE
nginx-ingress   nginx   aplicacion.com    192.168.49.2    80      13m
```
Y, tras mapear en el archivo /etc/hosts la dirección IP al dominio aplicacion.com, que es el dominio que hemos definido en el archivo [serviciosEspecializados.yaml](./serviciosEspecializados.yaml), se puede acceder localmente a la aplicación mediante el dominio.

```bash 
curl aplicacion.com/tiempo/Bilbao
{"maxima":16,"mensaje":"Prevision de temperaturas en BILBAO","minima":9}
```


### Implementación en servidor cloud

Para ejecutar la aplicación en un servidor cloud se ha usado Microsoft Azure. Para ello, tras crearnos la cuenta de estudiante, hemos creado un grupo de recursos y un clúster de Kubernetes. 

A continuación, para manejar de manera local el clúster de Kubernetes, hemos instalado la CLI de Azure, hemos hecho login con `az login`, establecido la suscripción del cluster con el comando `az account set --subscription <id> ` y nos descargamos las credenciales del clúster con el comando `az aks get-credentials --resource-group <nombre_grupo> --name <nombre_cluster>`, con esto modificamos el contexto de kubectl para que apunte al clúster de Azure, esto se encuentra en el archivo `~/.kube/config`.

Ahora, al ejecutar `kubectl get nodes` deberíamos ver los nodos del clúster de Azure.

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

En un principio estabamos usando un servicio NodePort, y al estar trabajando con un servicio cloud, para acceder a la aplicación necesitamos saber la IP pública uno de los nodos y el puerto que se ha asignado al servicio. Para ello, ejecutamos el comando `kubectl get services` y buscamos el servicio que nos interesa. No obstante, por defecto los nodos en AKS solo tienen IPs privadas, por lo que los servicios de tipo NodePort no serán accesibles desde fuera del clúster, ver https://learn.microsoft.com/en-us/answers/questions/200402/how-to-publish-services-on-aks-with-nodeport-servi

Por lo tanto, decidimos cambiar el servicio a uno de tipo LoadBalancer, que nos proporciona una IP pública para acceder a la aplicación y, además, actúa como balanceador de carga no solo para los pods del servicio, sino también para los nodos (que en este caso hay dos). Para ello, modificamos el archivo [serviciosIdenticos.yaml](./serviciosIdenticos.yaml) y cambiamos el tipo de servicio a LoadBalancer.

Ahora, al ejecutar el comando `kubectl get services` deberíamos ver la IP pública asignada al servicio.

```bash
kubectl get svc
NAME            TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)        AGE
kubernetes      ClusterIP      10.0.0.1       <none>           443/TCP        5h17m
nginx-service   LoadBalancer   10.0.162.168   172.214.13.251   80:32199/TCP   3m1s
```

Ahora se puede acceder globalmente a la aplicación mediante la IP pública que se nos ha asignado. Por ejemplo, si queremos acceder al servicio de predicción de temperaturas en Donostia:

```bash
curl 172.214.13.251/tiempo/donostia
{"maxima":16,"mensaje":"Prevision de temperaturas en DONOSTIA","minima":10}
```


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
nginx-ingress   nginx   aplicacion.com    57.151.8.80     80      13m
```

Ahora que sabemos la dirección IP, podemos mapear en el archivo /etc/hosts la dirección IP al dominio aplicacion.com, que es el dominio que hemos definido en el archivo [serviciosEspecializados.yaml](./serviciosEspecializados.yaml), y acceder a la aplicación desde el navegador. Para que la aplicación sea accesible por todo el mundo solo nos haria falta contratar un dominio y asignarle la dirección IP que nos ha proporcionado Azure.

```bash
curl aplicacion.com/tiempo/Bilbao
{"maxima":16,"mensaje":"Prevision de temperaturas en BILBAO","minima":9}
```

