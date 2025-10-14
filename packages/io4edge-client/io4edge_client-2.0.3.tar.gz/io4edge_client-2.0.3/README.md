# io4edge-client-python
python client sdk for io4edge.

[io4edge devices](https://docs.ci4rail.com/edge-solutions/io4edge/) are intelligent I/O devices invented by [Ci4Rail](https://www.ci4rail.com), connected to the host via network.

This library provides support for the following function blocks within io4edge devices:
* io4edge management functions, such as firmware update
* Analog In TypeA - IOU01, MIO01
* Analog In TypeB - IOU09, MIO09
* Binary IO TypeA - IOU01, MIO01
* CAN Layer2 - IOU03, MIO03, IOU04, MIO04, IOU06
* MVB Sniffer - IOU03, MIO03
* Binary IO TypeB - IOU06, EKF SQ1, EKF SQ3
* Binary IO TypeC - IOU07
* Bitbus Sniffer - IOU13
* Digiwave - IOU13
* Binary IO TypeD - EKF SQ1
* Pixel Display - EKF SQ3
* Color LED - EKF Z1010
* Watchdog - EKF Z1010

Currently not supported, but will follow:
* Motion Sensor - CPU01UC


## Installation

```bash
pip3 install io4edge_client
```

### Usage

See [examples in github repo](https://github.com/ci4rail/io4edge-client-python) for usage examples.


### Running in Docker

To run the examples in a docker container, you can use the provided `Dockerfile` in `examples/docker` directory.

In the Dockerfile, Replace `dumpstream.py` script with your python application path.

To build the docker image, run the following command on your host to build it for your target platform, in this case the target platform  `linux/arm64`:

```bash
docker buildx build --platform linux/arm64  -f examples/docker/Dockerfile . --push -t <your-docker-image-name>:<version>
```

On your target platform, run the container in the host network, so that you can use the service names of the io4edge devices:
```
docker run --network=host <your-docker-image-name>:<version> <parameters-to-your-python-script>
```

## Releasing

To release a new version of the package, follow these steps:
1. Update the version number in `io4edge-client/version.py`.
2. Create a new git tag with the same version number, e.g. `git tag v1.0.0`.
3. Push the tag to the remote repository: `git push --tags`.

## Copyright

Copyright © 2021-2025 Ci4Rail GmbH <engineering@ci4rail.com>

io4edge_client_python package is released under Apache 2.0 License, see [LICENSE](LICENSE) for details.
