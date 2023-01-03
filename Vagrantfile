Vagrant.configure("2") do |config|
  config.vm.define "web1" do |web|
    web.vm.box = "ubuntu/focal64"
    web.vm.network "private_network", ip: "192.168.50.101"
    web.vm.provision "shell", path: "install_web.sh", args: "web1"
  end

  config.vm.define "web2" do |web|
    web.vm.box = "ubuntu/focal64"
    web.vm.network "private_network", ip: "192.168.50.102"
    web.vm.provision "shell", path: "install_web.sh", args: "web2"
  end

  config.vm.define "web3" do |web|
    web.vm.box = "ubuntu/focal64"
    web.vm.network "private_network", ip: "192.168.50.103"
    web.vm.provision "shell", path: "install_web.sh", args: "web3"
  end
end
