# Thought Process
- This is used car prices in saudi arabia.
- Usually in car world, the used car prices heavily influenced by the new price when it's bought.
  And these features will likely correlate to the new price:
  - Car's type and maker
  - Options
  - Engine size
    - Probably not always the case, it's the delivered power that matters, we're still missing
      data like turbo, awd/fwd/rwd, even better if we have the horsepower data
- Now we're talking about price depreciation. It's always correlated by demand. And demand will usually
  correlate to:
  - Car's maker -> reputable brands will hold the price better than less known/new brands
  - Gear Type -> automatic is usually preferred by majority, but we have many supplies, let's see
    if this matters or not
  - Year & Mileage -> consumers will always prefer used car that feels new
- The rest of the features probably doesn't determine its price, these are:
  - Region
  - Origin
- Zero price isn't useful at all, we'll take that out

# Business Use Case
Simple, determining the price based on user's input. This will be helpful for used car sellers that are going
to buy used car from the owner. Determine its margin, then determine its selling price.

But because of the data limitation on not having all the car's new prices, we can't predict car's used price 
if the car's maker and type are not in the data. For example, we can't really predict Lamborghini Aventador 
used price because we don't have the data at all.
