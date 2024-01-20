#!/bin/bash
tmp_dir='/home/matias/devel/optimaix-maps/ms-cloud-allocation/gnn-experiments/gnn_v1/4tier/uqsim_logs'
mkdir -p $tmp_dir

numConns=320
end_sim=60
mon_interval=0
max_threads=8
max_cores=8

deploymnet=(cloud edge_cloud edge_fog_cloud edge_fog edge)

nginx_threads=($(seq 1 1 $max_threads))
memcached_threads=($(seq 1 1 $max_threads))
php_threads=($(seq 1 1 $max_threads))
phpio_threads=($(seq 1 1 $max_threads))
mongodb_threads=($(seq 1 1 $max_threads))
mongoio_threads=($(seq 1 1 $max_threads))

nginx_cores=($(seq 1 1 $max_cores))
memcached_cores=($(seq 1 1 $max_threads))
php_cores=($(seq 1 1 $max_threads))
phpio_cores=($(seq 1 1 $max_threads))
mongodb_cores=($(seq 1 1 $max_threads))
mongoio_cores=($(seq 1 1 $max_threads))

kqps=(1 2 3 4 5 6 7 8 9 10)

for c in ${deploymnet[@]}
do
	machineFile='machines_'$c'.py'
	for k in ${kqps[@]} 
	do
		for i in ${nginx_threads[@]}
		do
			for j in ${memcached_threads[@]}
			do
				for l in ${php_threads[@]}
				do
					for m in ${phpio_threads[@]} 
					do
						for n in ${mongodb_threads[@]} 
						do
							for o in ${mongoio_threads[@]} 
							do
								for p in ${nginx_cores[@]} 
								do
									for q in ${memcached_cores[@]} 
									do
										for r in ${php_cores[@]} 
										do
											for s in ${phpio_cores[@]} 
											do
												for t in ${mongodb_cores[@]} 
												do
													for u in ${mongoio_cores[@]} 
													do
														echo Executing $c $k $i $j $l $m $n $o $p $q $r $s $t $u
														cd ./architecture/4tier_nginx_rpc/
														python3 'start_architecture.py' '--end_seconds' $end_sim '--monitor_interval' $mon_interval '--machinesFile' $machineFile '--ngxThreads' $i '--phpThreads' $l '--phpIOThreads' $m '--mmcThreads' $j '--mongoThreads' $n '--mongoIOThreads' $o '--ngxCores' $p '--phpCores' $r '--phpIOCores' $s '--mmcCores' $q '--mongoCores' $t '--mongoIOCores' $u
														cd ../../
														filename=$tmp_dir'/''deployment_'$c'_kqps_'$k'_ngx_'$i'_mmc_'$j'_php_'$l'_phpio_'$m'_mongo_'$n'_mongoio_'$o'_ngxcores_'$p'_mmccores_'$q'_phpcores_'$r'_phpiocores_'$s'_mongocores_'$t'_mongoiocores_'$u'.out'
														touch $filename
														./microsim ./architecture/4tier_nginx_rpc/json/ $numConns expo $k > $filename
														echo DONE
													done
												done
											done
										done
									done
								done
							done
						done
					done
				done
			done
		done
	done
done
