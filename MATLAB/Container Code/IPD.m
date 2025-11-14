clear all;

%Ingredient Probability Distribution
run("DataParser.m");

%Probability Calculations
for i = 1:length(ingredients)
    ingredients(i).probability = 0;
end

for i = 1:length(recipes)
    n_1 = numID(recipes(i).ingredient_1);
    n_2 = numID(recipes(i).ingredient_2);
    n_3 = numID(recipes(i).ingredient_3);
    if n_1 > 0
        ingredients(n_1).probability = ingredients(n_1).probability + recipes(i).probability;
    end
    if n_2 > 0
        ingredients(n_2).probability = ingredients(n_2).probability + recipes(i).probability;
    end
    if n_3 > 0
        ingredients(n_3).probability = ingredients(n_3).probability + recipes(i).probability;
    end
end

%Modeling Probability Distributions for Ingredients
for i = 1:length(ingredients)
    ingList(i) = ingredients(i).name + " (" + ingredients(i).id + ")";
    ingProb(i) = ingredients(i).probability;
end

bar(ingList, ingProb*100);
set(gca, 'YTick', 0:5:100);
ylim([0 100]);
ylabel("Ingredient Probability (%)");
xlabel("Ingredients");
title("Ingredient Probability Distribution");
grid on;

%Volume Calculations
n = 100;    %Theoretical amount of people that will use Booz-E

for i = 1:length(ingredients)
    ingredients(i).volume = 0;
end

for i = 1:length(recipes)
    n_1 = numID(recipes(i).ingredient_1);
    n_2 = numID(recipes(i).ingredient_2);
    n_3 = numID(recipes(i).ingredient_3);
    if n_1 > 0
        ingredients(n_1).volume = ingredients(n_1).volume + n*recipes(i).probability*recipes(i).amount_1;
    end
    if n_2 > 0
        ingredients(n_2).volume = ingredients(n_2).volume + n*recipes(i).probability*recipes(i).amount_2;
    end
    if n_3 > 0
        ingredients(n_3).volume = ingredients(n_3).volume + n*recipes(i).probability*recipes(i).amount_3;
    end
end

%Modeling Volume
for i = 1:length(ingredients)
    ingVol(i) = ingredients(i).volume;
end

figure;
bar(ingList, ingVol);
set(gca, 'YTick', 0:250:4000);
ylim([0 4000]);
ylabel("Volume (mL)");
xlabel("Ingredients")
title("Volume needed for " + n + " customers");
grid on;
