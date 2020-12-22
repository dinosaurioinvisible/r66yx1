
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

                % 3.1 - Model of population of neurons

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% fi(theta) = G * exp (beta (cos (2 (theta - theta_i)) -1)) + K
% fi(theta) is the mean spike count of a neuron as a function of theta

G = 60;                          % G = maximal firing rate (G = 60 spikes/s)
beta = 4;                        % beta = the concentration parameter
K = 5;                           % K = spontaneous activity (K = 5 spikes/s)
N = 50;                          % N = the population of neurons
por_0 = -90;                     % por_start = initial preferred orientation
por_n = 90;                      % por_end = last preferred orientation
delta_i = (por_n-por_0)/(N-1);   % i = space between preferred orientation of neurons
theta_i = por_0:delta_i:por_n;   % preferred orientations, equally spaced between -90 and 90 deg 

% 3.1.a
% plot the mean response f(theta_0) of the population of neurons for:

% the stimulus can be 0 or 30 degrees
theta0 = 0;
theta1 = 30;

% the variability (noise) of the spike count is poisson
%theta0 = poirv(N, theta);

% f for the population size N 
fi_theta0 = G * exp (beta * (cos(2 * degtorad( theta0 - theta_i)) -1)) + K;
fi_theta1 = G * exp (beta * (cos(2 * degtorad( theta1 - theta_i)) -1)) + K;

% 3.1.b
% plot an example of the population response r_theta for theta = 0, 30

% response population
r_theta0 = [];
r_theta1 = [];

for i = theta_i,
    ri_theta0 = G * exp (beta * (cos(2 * degtorad( theta0 - i)) -1)) + K;
    ri0_est = poirv(1, ri_theta0);
    r_theta0 = [r_theta0 ri0_est];
    ri_theta1 = G * exp (beta * (cos(2 * degtorad( theta1 - i)) -1)) + K;
    ri1_est = poirv(1, ri_theta1);
    r_theta1 = [r_theta1 ri1_est];
end

% Population response plot
Population_response_plot = figure;
subplot(2,1,1)
plot(theta_i, fi_theta0);
hold on 
plot(theta_i, r_theta0);
hold on
plot([-90 90],[K K],'--')
plot([-90 90],[G+K G+K],'--')
plot([theta0 theta0],[0 90],'--')
xlim([-90, 90])
ylim([0, 90])
title('Population response to stimulus (0 degrees)','FontSize',12)
ylabel('Spike count (spk/s)','FontSize',12)
xlabel('Neurons preferred orientation (degrees)','FontSize',12)
subplot(2,1,2)
plot(theta_i, fi_theta1);
hold on
plot(theta_i, r_theta1);
hold on
plot([-90 90],[K K],'--')
plot([-90 90],[G+K G+K],'--')
plot([theta1 theta1],[0 90],'--')
xlim([-90, 90])
ylim([0, 90])
title('Population response to stimulus (30 degrees)','FontSize',12)
ylabel('Spike count (spk/s)','FontSize',12)
xlabel('Neurons preferred orientation (degrees)','FontSize',12)
%saveas(gcf, '/afs/inf.ed.ac.uk/user/s16/s1670175/Desktop/plot3.1.png', 'png')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        % 3.2 - Setting the satge: winner take-all decoding

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 3.2.a
% implement the WTA 
% try it using simulated population responses like in 3.1 (theta = 0 and 30)
% can you recover the orientation of the stimulus?

% given that we know the preferred orientations for all neurons, we just
% need to chooose the orientations associated with the max response

max = 0;

for i = 1:length(r_theta0),
    if (r_theta0(i) > max)
        max = r_theta0(i);
        theta0_est = theta_i(i);
    end
end

theta0_est_bias = theta0_est - theta0;

% to check that it works for theta0
% r_theta0
% theta0_est
% theta0_est_bias

max = 0;

for i = 1:length(r_theta1),
    if (r_theta1(i) > max)
        max = r_theta1(i);
        theta1_est = theta_i(i);        
    end
end

theta1_est_bias = theta1_est - theta1;

% to check that it works for theta1
% r_theta1
% theta1_est
% theta1_est_bias


% 3.2.b
% vary the stimulus orientation (theta) from -90 to 90
% for each stimulus direction, compute theta_est 150 times
% and the average over the 150 repetitions

theta_est_bias = [];
theta_est_var = [];

% stimulus variation from -90 to 90 degrees (theta_x)
theta_x = -90:10:90;

% for each orientation (theta) in -90 to 90 range (theta_x)
% simulate population response for each neuron preferred orientation
% decode response using WTA and estimate the stimulus (theta_est)
% compare WTA estimates with the original stimuli (theta_est_bias)
% compute the variance of the estimator 
for theta = theta_x,   
    
    theta_est_reps = [];
    
    for repetition = 1:150,                                          
        
        % simulated response for each neuron preferred orientation (i)
        r_theta = [];
        for i = theta_i,
            ri_theta = G * exp (beta * (cos(2 * degtorad( theta - i)) -1)) + K;
            ri_sim = poirv(1, ri_theta);
            r_theta = [r_theta ri_sim];        
        end
    
        % estimation of theta (theta_est) given a simulated response r(theta)
        max = 0;
        for r = 1:length(r_theta),
            if (r_theta(r) > max)
                max = r_theta1(r);
                theta_est_r = theta_i(r);                            
            end
        end        
        
        % the list of all theta_est for each repetition of theta
        theta_est_reps = [theta_est_reps theta_est_r];                           
    end
    
    % bias and variance of theta_est given the 150 repetitions of theta
    theta_est_average = sum(theta_est_reps)/length(theta_est_reps);
    theta_est_bias_theta = theta_est_average - theta;  
    theta_est_var_theta = var(circ_mean(theta_est_reps));           
    
    % the list of biases and variances for each theta
    theta_est_bias = [theta_est_bias theta_est_bias_theta];
    theta_est_var = [theta_est_var theta_est_var_theta];    
end

% 3.2.c
% Plot the bias of the estimator as a function of theta
% 3.2.d
% Plot the variance of the estimator as a function of theta

% WTA estimator bias
WTA_estimator_bias__variance_plot = figure;
subplot(2,1,1)
plot(theta_x, circ_mean(theta_est_bias));
hold on
plot([-90 90],[0 0],'--')
xlim([-90, 90])
ylim([-10, 10])
title('WTA estimator bias','FontSize',12)
ylabel('Estimator bias (degrees)','FontSize',8)
xlabel('Stimulus orientation (degrees)','FontSize',8)
subplot(2,1,2)
plot(theta_x, theta_est_var);
hold on
plot([-90 90],[0 0],'--')
xlim([-90, 90])
ylim([0, 10])
title('WTA estimator variance','FontSize',12)
ylabel('Estimator variance (degrees)','FontSize',8)
xlabel('Stimulus orientation (degrees)','FontSize',8)
%saveas(gcf, '/afs/inf.ed.ac.uk/user/s16/s1670175/Desktop/plot3.2.png', 'png')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 3.3 - Towards a better estimate of the orientation of the stimulus: 
%                           Population Vector

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% 3.3.a
% Implement the population vector and check it works
% Vary theta from -90 to 90 and for each stimulus direction
% compute theta_est for 150 repetitions of theta
% and the average over the 150 repetitions
% plot the bias and the variance of theta_est as a function of theta

psin_theta = 0;
pcos_theta = 0;

for i = 1:length(r_theta1),
    % response for each stimuli theta
    ri = r_theta1(i);
    % theta_est given each response
    theta_est_i = degtorad(theta_i(i));    
    
    psin_theta = psin_theta + (ri * sin(2 * theta_est_i));
    pcos_theta = pcos_theta + (ri * cos(2 * theta_est_i));    
end

theta_est = radtodeg((1/2) * atan( psin_theta/pcos_theta));

% to check it works for theta1
% theta1
% r_theta1
% theta_est


% vary the stimulus orientation (theta) from -90 to 90
% for each stimulus direction, compute theta_est 150 times
% and the average over the 150 repetitions

theta_est_bias = [];
theta_est_var = [];

% stimulus variation from -90 to 90 degrees (theta_x)
theta_x = -90:10:90;

% for each orientation (theta) in -90 to 90 range (theta_x)
% simulate population response for each neuron preferred orientation
% decode response using WTA and estimate the stimulus (theta_est)
% compare WTA estimates with the original stimuli (theta_est_bias)
% compute the variance of the estimator 
for theta = theta_x,   
    
    theta_est_reps = [];
    
    for repetition = 1:150,                                          
        
        % simulated response for each neuron preferred orientation (i)
        r_theta = [];
        for i = theta_i,
            ri_theta = G * exp (beta * (cos(2 * degtorad( theta - i)) -1)) + K;
            ri_sim = poirv(1, ri_theta);
            r_theta = [r_theta ri_sim];        
        end
    
        % estimation of theta (theta_est) given a simulated response r(theta)
        psin_theta = 0;
        pcos_theta = 0;

        for i = 1:length(r_theta),
            % response for each stimuli theta
            ri = r_theta(i);
            % theta_est given each response
            theta_est_i = degtorad(theta_i(i));    
    
            psin_theta = psin_theta + (ri * sin(2 * theta_est_i));
            pcos_theta = pcos_theta + (ri * cos(2 * theta_est_i));    
        end

        theta_est_r = radtodeg((1/2) * atan( psin_theta/pcos_theta));   
        
        % the list of all theta_est for each repetition of theta
        theta_est_reps = [theta_est_reps theta_est_r];                           
    end
    
    % bias and variance of theta_est given the 150 repetitions of theta
    theta_est_average = sum(theta_est_reps)/length(theta_est_reps);
    theta_est_bias_theta = theta_est_average - theta;  
    theta_est_var_theta = var(theta_est_reps);    
    
    % the list of biases and variances for each theta
    theta_est_bias = [theta_est_bias theta_est_bias_theta];
    theta_est_var = [theta_est_var theta_est_var_theta];    
end


% Plot the bias of the estimator as a function of theta
% Plot the variance of the estimator as a function of theta

% Population vector estimator bias
PV_estimator_bias__variance_plot = figure;
subplot(2,1,1)
plot(theta_x, circ_mean(theta_est_bias));
hold on
plot([-90 90],[0 0],'--')
xlim([-90, 90])
ylim([-10, 10])
title('Population vector bias','FontSize',12)
ylabel('Estimator bias (degrees)','FontSize',8)
xlabel('Stimulus orientation (degrees)','FontSize',8)
subplot(2,1,2)
plot(theta_x, theta_est_var);
hold on
plot([-90 90],[0 0],'--')
xlim([-90, 90])
ylim([0, 10])
title('Population vector variance','FontSize',12)
ylabel('Estimator variance (degrees)','FontSize',8)
xlabel('Stimulus orientation (degrees)','FontSize',8)
%saveas(gcf, '/afs/inf.ed.ac.uk/user/s16/s1670175/Desktop/plot3.3.png', 'png')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 3.4 - Maximum Likelihood (ML) estimator and Maximum a Posteriori (MAP)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% 3.4.a
% Using the definition of Poisson variability write the mathematical
% expression for the log likelihood (lnP[r|theta]) of this model 
% as a function of f_i(theta) and r_i

% we know that maximum likelihood is given by
% theta_est = argmax_s(P(r|s))

% from the lecture slides wk2-1:
% P(n = k|s) = exp( -f(s)) * f(s)^k * (1/k!)

% from: http://statweb.stanford.edu/~susan/courses/s200/lectures/lect11.pdf
% P(X = x) = lambda^x * e^(-lamda) * (1/x!)

% given the independence assumption for poisson variables:
% L(lambda) = sum_i_n(X_i * log(lambda) - lambda - log(X_i!)
% L(lambda) = log(lambda)*sum_i_n(X_i) - n*lambda - sum_i_n(log(X_i!))

% now we can put this in terms of our current model, so:
% L(r|theta) = r * ln(f(theta)) - f(theta) - ln(r!)

% where the observed response (r) is: 
% r = {r1(theta) ... r50(theta)}, so:

% ln P(r_i|theta) = sum_i_n(r_i * ln(f_i(theta)) - f_i(theta) - ln(r_i!)
% ln P(r_i|theta) = sum_i_n(r_i) * ln(f_i(theta)) - n * f_i(theta) - sum_i_n(ln(r_i!))

% theta_est = argmax_theta(r|theta) 

% so that f_i(theta) would be the most probable tuning curve given r
% and theta_est the theta for that tuning curve

% 3.4.b 
% Implement the maximum likelihood decoder algorithm
% Try it out on a few trials to see if works
% Vary the stimulus orientation from -90 to 90 and for each theta
% compute the stimulus estimate for 50 repetitions of the stimulus 
% Plot the bias as a function of theta

for theta = -90:10:90,    
    
    theta_est_reps = [];
    
    for repetition = 1:150,           
        
        likelihood = 0;
        
        % simulated response for each neuron preferred orientation (i)
        r_theta = [];
        for i = theta_i,
            ri_theta = G * exp (beta * (cos(2 * degtorad( theta - i)) -1)) + K;
            ri_sim = poirv(1, ri_theta);
            r_theta = [r_theta ri_sim];        
        end
        
        for i = theta_i,

            fi_theta = G * exp (beta * (cos(2 * degtorad(theta - theta_i)) -1)) + K;    
            theta_logprob = sum(r_theta) * log(fi_theta) - N * fi_theta - sum(log(factorial(r_theta)));                    
                 
            %theta_likelihood = sum(ri_theta) * log(fi_theta)/ N;               
            
            if (theta_logprob < likelihood)
                likelihood = theta_likelihood;                        
                theta_est_r = i;
            else
                theta_est_r = theta;
            end
            
        end
        % the list of all theta_est for each repetition of theta
        theta_est_reps = [theta_est_reps theta_est_r];                           
    end
    
    % bias and variance of theta_est given the 150 repetitions of theta
    theta_est_average = sum(theta_est_reps)/length(theta_est_reps);
    theta_est_bias_theta = theta_est_average - theta;  
    theta_est_var_theta = var(theta_est_reps);    
    
    % the list of biases and variances for each theta
    theta_est_bias = [theta_est_bias theta_est_bias_theta];
    theta_est_var = [theta_est_var theta_est_var_theta];    
end


% MLE estimator bias
MLE_estimator = figure;
subplot(2,1,1)
plot(theta, circ_mean(theta_est_bias));
hold on
plot([-90 90],[0 0],'--')
%xlim([-90, 90])
%ylim([-10, 10])
title('MLE estimator bias','FontSize',12)
ylabel('Estimator bias (degrees)','FontSize',8)
xlabel('Stimulus orientation (degrees)','FontSize',8)
subplot(2,1,2)
plot(theta, theta_est_var);
hold on
plot([-90 90],[0 0],'--')
%xlim([-90, 90])
%ylim([0, 10])
title('MLE estimator variance','FontSize',12)
ylabel('Estimator variance (degrees)','FontSize',8)
xlabel('Stimulus orientation (degrees)','FontSize',8)
saveas(gcf, '/afs/inf.ed.ac.uk/user/s16/s1670175/Desktop/plot3.4.1.png', 'png')

% 3.4.c
% Choose a function that is suitable to model a prior 
% and parameters such that the resulting prior approximates figure 5A of
% the article
% Write the equation and plot it 

% 3.4.d
% Implement the maximum a posteriori (MAP) decoder algorithm 
% Check that the prior influences the estimation 

% 3.4.e 
% Show the bias and variance 
% Does this model have the potential to explain psichophysics biases?


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 3.5 - Effect of cell heterogenities on estimation and discrimination
%       performaces

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%from: https://en.wikipedia.org/wiki/Von_Mises_distribution#Limiting_behavior

% 3.5.a 
% Plot the von Mises distribution mentioned in Girshick et al. 
% 3.5.b 
% Draw 50 samples from this distribution for the preferred orientations
% of your new population of neurons

% k = beta
beta = 3.3;
% distribution is clustered around mu
mu = 0;
% our x
x = 0;
% bassels modified equation % I couldn't implement it
% I0
% standard deviation, sigma = 35;
sd1 = rand * sigma/2;
sd2 = rand * sigma/2;
sd = sd1-sd2;

VM_dist = [];

for i = theta_i,    
    x = exp(beta * (cos (degtorad(i - mu+sd)))) / 2*pi*beta;
    VM_dist = [VM_dist x];    
end

%VM_dist

% Population response plot
VonMises = figure;
plot(theta_i, VM_dist)
hold on
plot([-90 90],[0 0],'--')
plot([0 0],[0 150],'--')
xlim([-90, 90])
ylim([0, 150])
title('Attempt for Von Mises ditribution','FontSize',12)
ylabel('sample','FontSize',12)
xlabel('range','FontSize',12)
%saveas(gcf, '/afs/inf.ed.ac.uk/user/s16/s1670175/Desktop/plot3.5.1.png', 'png')


% 3.5.c
% Use the population vector decoding method again

% Implement the population vector and check it works
% Vary theta from -90 to 90 and for each stimulus direction
% compute theta_est for 150 repetitions of theta
% and the average over the 150 repetitions
% plot the bias and the variance of theta_est as a function of theta


theta_est_bias = [];
theta_est_var = [];

for theta = theta_x,   
    
    theta_est_reps = [];
    
    for repetition = 1:150,                                          
        
        % simulated response for each neuron preferred orientation (i)
        r_theta = [];
        
        for i = VM_dist,
            ri_theta = G * exp (beta * (cos(2 * degtorad( theta - i)) -1)) + K;
            ri_sim = poirv(1, ri_theta);
            r_theta = [r_theta ri_sim];        
        end
    
        % estimation of theta (theta_est) given a simulated response r(theta)
        psin_theta = 0;
        pcos_theta = 0;

        for i = 1:length(r_theta),
            % response for each stimuli theta
            ri = r_theta(i);
            % theta_est given each response
            theta_est_i = degtorad(theta_i(i));    
    
            psin_theta = psin_theta + (ri * sin(2 * theta_est_i));
            pcos_theta = pcos_theta + (ri * cos(2 * theta_est_i));    
        end

        theta_est_r = radtodeg((1/2) * atan( psin_theta/pcos_theta));   
        
        % the list of all theta_est for each repetition of theta
        theta_est_reps = [theta_est_reps theta_est_r];                           
    end
    
    % bias and variance of theta_est given the 150 repetitions of theta
    theta_est_average = sum(theta_est_reps)/length(theta_est_reps);
    theta_est_bias_theta = theta_est_average - theta;  
    theta_est_var_theta = var(theta_est_reps);    
    
    % the list of biases and variances for each theta
    theta_est_bias = [theta_est_bias theta_est_bias_theta];
    theta_est_var = [theta_est_var theta_est_var_theta];    
end


% Plot the bias of the estimator as a function of theta
% Plot the variance of the estimator as a function of theta

% Population vector estimator bias
PV_estimator_VM_distribution_bias__variance_plot = figure;
subplot(2,1,1)
plot(theta_x, circ_mean(theta_est_bias));
hold on
plot([-90 90],[0 0],'--')
xlim([-90, 90])
ylim([-10, 10])
title('Population vector bias','FontSize',12)
ylabel('Estimator bias (degrees)','FontSize',8)
xlabel('Stimulus orientation (degrees)','FontSize',8)
subplot(2,1,2)
plot(theta_x, circ_mean(theta_est_var));
hold on
plot([-90 90],[0 0],'--')
xlim([-90, 90])
ylim([0, 10])
title('Population vector variance','FontSize',12)
ylabel('Estimator variance (degrees)','FontSize',8)
xlabel('Stimulus orientation (degrees)','FontSize',8)
%saveas(gcf, '/afs/inf.ed.ac.uk/user/s16/s1670175/Desktop/plot5.2.png', 'png')



