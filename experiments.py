#####################################################
                  # Example experiments
  #####################################################

  # Figure 3
  # 2-motor, 0-sensor IDSM
  # sim_time = 20
  # manually added 4 nodes in relative proximity
  # externally assigned 2 motor states
  # m1 = 0.75 * cos( (2π / 10) * t
  # m2 = 0.75 * sin( (2π / 10) * t
  def figure3(self, time=20, iw = [-500, -100, 0, 50, 100]):
      for iwx in iw:
          # nodes = [position, velocity, weight]
          n1 = [[0.55, 0.50], 0, iwx]
          n2 = [[0.50, 0.45], 0, 0]
          n3 = [[0.45, 0.50], 0, 0]
          n4 = [[0.50, 0.55], 0, 0]
          self.nodes.append(n1, n2, n3, n4)
          for t in range(1, time+1):
              self.idsm_fx()
              self.maintenance_fx()
              self.all_x.append(copy.deepcopy(self.x))
          # plot x, y
          plt.plot([node[0][0] for node in self.nodes],[node[0][1] for node in self.nodes])
          figname = "node_weight_fig3_{}".format(iwx)
          plt.savefig(figname)
          plt.close
          # plot weight influence
          # plt.plot()
          # figname = "influence_fig3_{}".format(iwx)
          # plt.savefig(figname)
          # plt.close

  # training
  # for the first 20 time units the robot is controlled by a training controller
  def training_fx(self, time=20):
      for t in range(1, time+1):
          # movement
          sensor = 1/(1+self.x**2)
          weight = 0
          velocity = np.array([np.cos(t/2)/2])
          self.x += velocity
          # self.x = copy.deepcopy([self.x[i]+velocity[i] for i in range(len(self.x))])
          # creation of nodes
          self.nodes.append([copy.deepcopy(self.x), velocity, weight])
          self.sensor_hist.append(sensor)
          # record for whole history
          self.all_x.append(copy.deepcopy(self.x))
      # plot
      plt.plot([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
      plt.scatter([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
      plt.xlabel("Time")
      plt.ylabel("Position")
      plt.savefig("_TrainingPlot")
      plt.close()

  # idsm control phase
  def operation(self):
      for t in range(self.sim_time):
          print(t)
          # self.sensory_fx()
          self.idsm_fx()
          self.maintenance_fx()
          self.all_x.append(copy.deepcopy(self.x))
      # sensory input
      plt.plot([t for t in range(len(self.sensor_hist))], [i for i in self.sensor_hist])
      plt.scatter([t for t in range(len(self.sensor_hist))], [i for i in self.sensor_hist])
      plt.savefig("_Sensors")
      plt.close()
      ###
      plt.plot([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
      plt.scatter([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
      plt.savefig("_AllNodesPlot")
      plt.close()
      # positions independently of the creation of the nodes
      plt.plot([t for t in range(len(self.all_x))], [i for i in self.all_x])
      plt.savefig("_AgentHistory")
      plt.close()
      ###
      ###
      ###
      plt.plot([t for t in range(len(self.why))], [i[0] for i in self.why])
      plt.scatter([t for t in range(len(self.why))], [i[0] for i in self.why])
      plt.savefig("__1densities")
      # plt.close()
      #
      plt.plot([t for t in range(len(self.why))], [i[1] for i in self.why])
      plt.scatter([t for t in range(len(self.why))], [i[1] for i in self.why])
      plt.savefig("__2motor_influence")
      # plt.close()
      #
      plt.plot([t for t in range(len(self.why))], [i[2] for i in self.why])
      plt.scatter([t for t in range(len(self.why))], [i[2] for i in self.why])
      plt.savefig("__3velocity")
      # plt.close()
      #
      plt.plot([t for t in range(len(self.why))], [i[3] for i in self.why])
      plt.scatter([t for t in range(len(self.why))], [i[3] for i in self.why])
      plt.savefig("__4attraction")
      # plt.close()
      #
      plt.plot([t for t in range(len(self.why))], [i[4] for i in self.why])
      plt.scatter([t for t in range(len(self.why))], [i[4] for i in self.why])
      plt.savefig("__5idsm")
      plt.close()

# run
# x = Agent()
# x.training_fx()
# x.operation()

# __main__
# if __name__ == "__main__":
#     main()
